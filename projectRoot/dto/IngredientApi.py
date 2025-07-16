import json
from typing import Optional, Dict, List, Tuple
from .SchemaApi import HealthinessInfo, SustainabilityInfo


class IngredientApi:

    """Rappresenta un ingrediente alimentare utilizzato nelle ricette (nel formato dell'API)."""

    def __init__(self, name: str, ingredients: List[Tuple[str, str]], healthiness: Optional[HealthinessInfo], sustainability: Optional[SustainabilityInfo], nutritional_values: Dict[str, float], food_item_url: Optional[str]):
        """
        Inizializza un oggetto istanza della classe IngredientApi.

        Args:
        - name : Nome dell'ingrediente.
        - ingredients : Lista di tuple con nome dell'ingrediente e quantità.
        - healthiness : Oggetto istanza della classe HealthinessInfo che descrive la salubrità dell'ingrediente.
        - sustainability : Oggetto istanza della classe SustainabilityInfo che descrive la sostenibilità dell'ingrediente.
        - nutritional_values : Dizionario dei valori nutrizionali dell'ingrediente.
        - food_item_url : fonte di origine del dato.
        """
        self.name = name
        self.ingredients = ingredients
        self.healthiness = healthiness
        self.sustainability = sustainability
        self.nutritional_values = nutritional_values
        self.food_item_url = food_item_url


    def to_dict(self):
        """
        Converte l'oggetto IngredientApi in un dizionario.

        Returns:
        - dict: Rappresentazione dell'oggetto in formato dizionario.
        """
        return {
            "food_item": self.name,
            "ingredients": {
                "ingredients": [name for name, _ in self.ingredients],
                "quantities": [quantity for _, quantity in self.ingredients]
            } if self.ingredients else None,
            "healthiness": self.healthiness.to_dict() if self.healthiness else None,
            "sustainability": self.sustainability.to_dict() if self.sustainability else None,
            "nutritional_values": self.nutritional_values,
            "food_item_url": self.food_item_url
        }

    def to_json(self):
        """
        Serializza l'oggetto in formato JSON.

        Returns:
        - str: Rappresentazione JSON dell'oggetto.
        """
        return json.dumps(self.to_dict())

    def from_food_info_dict(self, food_info):
        """
        Popola l'oggetto IngredientApi a partire da un dizionario.

        Args:
        - food_info : Dizionario contenente le informazioni dell'ingrediente nel formato atteso.
        """
        self.name = food_info.get("food_item", "")

        ingr_data = food_info.get("ingredients")
        if ingr_data is None:
            self.ingredients = []
        else:
            names = ingr_data.get("ingredients", [])
            quants = ingr_data.get("quantities", [])
            self.ingredients = list(zip(names, quants)) if quants else [(n, "") for n in names]

        h_data = food_info.get("healthiness", {})
        s_data = food_info.get("sustainability", {})
        self.healthiness = HealthinessInfo.from_dict(h_data) if h_data else None
        self.sustainability = SustainabilityInfo.from_dict(s_data) if s_data else None

        nutr = food_info.get("nutritional_values")
        if nutr is None:
            self.nutritional_values = {}
        else:
            self.nutritional_values = {k: float(v) for k, v in nutr.items()}

        self.food_item_url = food_info.get("food_item_url", "")


    def display(self):
        """
        Stampa una rappresentazione formattata dell'ingrediente.
        """
        print("\n" + "-" * 90)
        print(f"\nName : {self.name}")

        print(f"\nHealthiness Score: {self.healthiness.score if self.healthiness else 'N/A'}")
        if self.healthiness and self.healthiness.qualitative:
            print(f"  • Qualitative: {self.healthiness.qualitative}")

        print(f"\nSustainability Score: {self.sustainability.score if self.sustainability else 'N/A'}")
        if self.sustainability:
            if self.sustainability.qualitative:
                print(f"  • Qualitative: {self.sustainability.qualitative}")
            if self.sustainability.CF is not None:
                print(f"  • CF: {self.sustainability.CF}")
            if self.sustainability.WF is not None:
                print(f"  • WF: {self.sustainability.WF}")

        if self.ingredients:
            print("\nIngredients:")
            for ingrediente, quantita in self.ingredients:
                print(f"  - {ingrediente}: {quantita}")
        else:
            print("\nIngredients: N/A")

        print("\nNutritional Values:")
        for nutriente, valore in self.nutritional_values.items():
            print(f"  • {nutriente}: {valore}")

        print(f"\nURL : {self.food_item_url}")

        print("-" * 90)