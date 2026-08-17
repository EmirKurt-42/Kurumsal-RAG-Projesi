"""
Giris noktasi: terminalde soru-cevap dongusu.
"""
from container import Container


def main():
    container = Container()
    print("Hazır! Çıkmak için 'q' yaz.\n")

    while True:
        question = input("Soru: ").strip()
        if question.lower() == "q":
            break
        if not question:
            continue

        print("İlgili bilgiler aranıyor ve modele soruluyor...")
        try:
            chunks, answer = container.answer_question.execute(question)
        except Exception as e:
            print(f"\nHATA: {e}\n")
            continue

        print(f"\n--- CEVAP ---\n{answer}\n")
        if chunks:
            print("--- KAYNAKLAR ---")
            for c in chunks:
                print(f"- [{c['source']}] {c['title']} ({c['url']})")
        print("\n" + "=" * 50 + "\n")


if __name__ == "__main__":
    main()