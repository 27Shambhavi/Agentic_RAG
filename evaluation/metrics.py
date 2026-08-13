def exact_match(prediction: str, expected: str) -> bool:
    return prediction.strip().lower() == expected.strip().lower()
