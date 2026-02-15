from utils.evaluator import ContentEvaluator

# Initialize the evaluator
evaluator = ContentEvaluator()

# Test Case 1: Marketing Copy
print("=" * 60)
print("TEST 1: Marketing Copy Evaluation")
print("=" * 60)

marketing_content = """
¡Celebra el Día de las Madres con Amazon!

Sorprende a mamá con regalos que le encantarán. Desde tecnología hasta belleza, 
encuentra el regalo perfecto para demostrarle cuánto la quieres. 

🎁 Envío gratis en pedidos elegibles
💝 Envoltorio de regalo disponible
⭐ Miles de opciones con reseñas de 5 estrellas

Compra ahora y haz que este Día de las Madres sea inolvidable.
"""

result1 = evaluator.evaluate_content(
    content=marketing_content,
    use_case="marketing_copy",
    context="Mother's Day campaign for Spanish-speaking US customers"
)

print(f"\nOverall AI Score: {result1.ai_overall_score}/5.0")
print(f"Decision: {result1.ai_decision}")
print("\nDetailed Scores:")
for criterion_key, score_obj in result1.ai_scores.items():
    print(f"\n{criterion_key}: {score_obj.score}/5.0")
    print(f"  Explanation: {score_obj.explanation}")

# Test Case 2: Bilingual Compliance
print("\n" + "=" * 60)
print("TEST 2: Bilingual Compliance Evaluation")
print("=" * 60)

bilingual_content = """
WARNING / AVERTISSEMENT

Keep away from children under 3 years.
Small parts - choking hazard.

Tenir éloigné des enfants de moins de 3 ans.
Petites pièces - risque d'étouffement.

BATTERY SAFETY / SÉCURITÉ DES PILES
Do not dispose in fire.
Ne pas jeter au feu.
"""

result2 = evaluator.evaluate_content(
    content=bilingual_content,
    use_case="bilingual_compliance",
    context="Toy product warning label for Canadian market (English/French)"
)

print(f"\nOverall AI Score: {result2.ai_overall_score}/5.0")
print(f"Decision: {result2.ai_decision}")
print("\nDetailed Scores:")
for criterion_key, score_obj in result2.ai_scores.items():
    print(f"\n{criterion_key}: {score_obj.score}/5.0")
    print(f"  Explanation: {score_obj.explanation}")

print("\n" + "=" * 60)
print("Tests completed successfully!")
print("=" * 60)