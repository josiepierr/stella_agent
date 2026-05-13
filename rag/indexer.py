"""
indexer.py
Indexe les documents Stellantis dans ChromaDB pour la recherche sémantique RAG.

Usage : python indexer.py
"""

import json
import os
import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader

# ──────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR   = os.path.join(BASE_DIR, "docs_stellantis")
CHROMA_DIR = os.path.join(BASE_DIR, "chroma_db")

COLLECTION_NAME = "stellantis_docs"
CHUNK_SIZE      = 500   # caractères par chunk
CHUNK_OVERLAP   = 100   # chevauchement entre chunks


# ──────────────────────────────────────────────
# CHUNKING
# ──────────────────────────────────────────────

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    Découpe un texte en chunks avec chevauchement.
    Le chevauchement évite de perdre le contexte aux jonctions.
    """
    chunks = []
    start  = 0

    while start < len(text):
        end = start + chunk_size

        # Essayer de couper à une fin de phrase ou de ligne
        if end < len(text):
            for sep in ["\n\n", "\n", ". ", " "]:
                pos = text.rfind(sep, start, end)
                if pos > start + chunk_size // 2:
                    end = pos + len(sep)
                    break

        chunk = text[start:end].strip()
        if len(chunk) > 50:  # Ignorer les chunks trop courts
            chunks.append(chunk)

        start = end - overlap

    return chunks


# ──────────────────────────────────────────────
# CHARGEMENT DES DOCUMENTS
# ──────────────────────────────────────────────

def load_documents() -> list[dict]:
    """Charge les fichiers JSON, PDF et TXT du dossier docs_stellantis."""
    docs = []

    if not os.path.exists(DOCS_DIR):
        print(f"❌ Dossier {DOCS_DIR} introuvable.")
        return docs

    files = [
        f for f in os.listdir(DOCS_DIR)
        if f.lower().endswith((".json", ".pdf", ".txt"))
    ]

    print(f"📂 {len(files)} fichiers trouvés dans {DOCS_DIR}")

    for filename in files:
        filepath = os.path.join(DOCS_DIR, filename)
        ext = filename.lower().split(".")[-1]

        try:
            if ext == "json":
                with open(filepath, "r", encoding="utf-8") as f:
                    raw = json.load(f)

                # Cas JSON classique avec champ contenu
                if "contenu" in raw:
                    docs.append(raw)

                # Cas Swagger / OpenAPI
                elif "openapi" in raw or "paths" in raw:
                    text = json.dumps(raw, ensure_ascii=False, indent=2)
                    docs.append({
                        "marque": "Stellantis",
                        "categorie": "api",
                        "titre": raw.get("info", {}).get("title", filename),
                        "url": raw.get("servers", [{}])[0].get("url", ""),
                        "source_type": "official_public",
                        "contenu": text
                    })

            elif ext == "pdf":
                reader = PdfReader(filepath)
                pages_text = []

                for page_num, page in enumerate(reader.pages, start=1):
                    text = page.extract_text() or ""
                    if text.strip():
                        pages_text.append(f"\n--- Page {page_num} ---\n{text}")

                full_text = "\n".join(pages_text)

                docs.append({
                    "marque": "Stellantis",
                    "categorie": "official_pdf",
                    "titre": filename.replace(".pdf", ""),
                    "url": filepath,
                    "source_type": "official_public_pdf",
                    "contenu": full_text
                })

            elif ext == "txt":
                with open(filepath, "r", encoding="utf-8") as f:
                    text = f.read()

                docs.append({
                    "marque": "Stellantis",
                    "categorie": "official_text",
                    "titre": filename.replace(".txt", ""),
                    "url": filepath,
                    "source_type": "official_public_text",
                    "contenu": text
                })

        except Exception as e:
            print(f"  ⚠️ Erreur lecture {filename}: {e}")

    return docs


# ──────────────────────────────────────────────
# INDEXATION
# ──────────────────────────────────────────────

def index_documents():
    print("\n" + "="*55)
    print("  STELLA — Indexation base RAG ChromaDB")
    print("="*55 + "\n")

    # ── Initialisation ChromaDB
    print("🔧 Initialisation ChromaDB...")
    os.makedirs(CHROMA_DIR, exist_ok=True)
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # Fonction d'embedding — sentence-transformers (local, gratuit)
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="paraphrase-multilingual-MiniLM-L12-v2"
        # Modèle multilingue français/anglais, léger et efficace
    )

    # Supprimer la collection existante si elle existe (re-indexation propre)
    try:
        client.delete_collection(COLLECTION_NAME)
        print("  ♻️  Collection existante supprimée pour re-indexation")
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"}  # Similarité cosinus
    )
    print(f"  ✅ Collection '{COLLECTION_NAME}' créée\n")

    # ── Chargement des documents
    docs = load_documents()
    if not docs:
        print("❌ Aucun document à indexer. Lance d'abord scraper.py")
        return

    # ── Chunking et indexation
    print("📑 Découpage et indexation des documents...\n")
    total_chunks = 0

    for doc in docs:
        marque    = doc.get("marque", "Stellantis")
        categorie = doc.get("categorie", "general")
        titre     = doc.get("titre", "Document")
        contenu   = doc.get("contenu", "")
        url       = doc.get("url", "")

        if not contenu.strip():
            print(f"  ⚠️  Document vide ignoré : {titre}")
            continue

        chunks = chunk_text(contenu)
        print(f"  📄 {titre[:50]}...")
        print(f"     {len(contenu)} caractères → {len(chunks)} chunks")

        # Indexation chunk par chunk
        for i, chunk in enumerate(chunks):
            chunk_id = f"{marque}_{categorie}_{total_chunks + i}"

            collection.add(
                ids=[chunk_id],
                documents=[chunk],
                metadatas=[{
                    "marque":    marque,
                    "categorie": categorie,
                    "titre":     titre,
                    "url":       url,
                    "chunk_num": i,
                    "source":    f"{titre} (chunk {i+1}/{len(chunks)})"
                }]
            )

        total_chunks += len(chunks)
        print(f"     ✅ Indexé\n")

    # ── Test de la base
    print("="*55)
    print(f"✅ Indexation terminée :")
    print(f"   {len(docs)} documents indexés")
    print(f"   {total_chunks} chunks créés")
    print(f"   Base stockée dans : {CHROMA_DIR}")

    # Test rapide
    print("\n🧪 Test de recherche sémantique...")
    test_queries = [
        "STLA SmartCockpit logiciel véhicule connecté",
        "données véhicule connecté Mobilisights kilométrage consentement",
        "recommandations personnalisées recharge Free2move",
        "maintenance prédictive IA CloudMade",
        "API véhicule connecté Stellantis VIN odometer capteurs",
    ]
    for query in test_queries:
        results = collection.query(query_texts=[query], n_results=1)
        if results["documents"][0]:
            doc_found = results["documents"][0][0]
            meta      = results["metadatas"][0][0]
            print(f"\n  🔍 '{query}'")
            print(f"     → {meta['source']}")
            print(f"     → {doc_found[:100]}...")

    print(f"\n{'='*55}")
    print("👉 La base RAG est prête ! Stella peut maintenant")
    print("   répondre aux questions documentaires Stellantis.")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    index_documents()