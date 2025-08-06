import json
import requests

import dto.RecipeApi as rp
import dto.IngredientApi as ig
from service.domain import FoodHistoryService as fs
import service.bot.LangChainService as lcs
import Constants as p


HEADER = {"Content-Type": "application/json"}
URL_RECCOMENDATION = "http://localhost:8100/recommend"
URL_INFORMATION = "http://localhost:8100/food-info/"
URL_ALTERNATIVE = "http://localhost:8100/alternative"


def get_recipe_suggestion(mealDataJson, userData):
    """
    Restituisce un suggerimento alimentare in base ai dati dell'utente e alle informazioni della richiesta di raccomandazione.
    I dati vengono inviati al servizio di raccomandazione (POST API /recommend) e viene estratta la prima ricetta suggerita.

    Args:
    - mealDataJson : dizionario JSON con le informazioni della richiesta di raccomandazione.
    - userData : Oggetto utente, istanza della classe User.

    Returns:
    - RecipeApi or None: La ricetta suggerita, istanza della classe RecipeApi, oppure None in caso di errore.
    """
    
    # PRONTA MA NON FUNZIONA L'API
    """
    Parametri della chiamata /recommend API: 
      user_id : Unique identifier for the user
      preferences : List of food items, ingredients, or cuisines the user likes
      soft_restrictions : List of food items, ingredients, or cuisines the user dislikes
      hard_restrictions : List of specific food items to completely exclude from recommendations
      meal_time : What meal the user is looking for (breakfast, lunch, dinner, snack)
      previous_recommendations : List of previously recommended items to avoid repetition
      recommendation_count : Number of recommendations to return
      diversity_factor : Controls how diverse the recommendations should be (0.0-1.0)
      conversation_id : Identifier for the conversation these recommendations are associated with
    """
    
    if isinstance(mealDataJson, str):
      mealData = json.loads(mealDataJson)
    else:
      mealData = mealDataJson

    # recupera dal db la lista dei nomi delle ricette che l'utente ha consumato nell'ultima settimana
    previous_recommendations = []

    userHistory = fs.get_user_history_of_week(userData.id, False)
    if userHistory is not None and len(userHistory) > 0:
        for history in userHistory:
            previous_recommendations.append(history["recipe"]["name"])

    sus_defaul_restrictions = ['sustainability_score D','sustainability_score E']
    health_defaul_restrictions = ['nutri_score D','nutri_score E']
    hard_restrictions = userData.allergies + sus_defaul_restrictions + health_defaul_restrictions
    
    if(mealData['ingredients_desired'] ==[]):
      generated_ingredients = lcs.execute_chain(p.INGREDIENT_GENERATOR_PROMPT.format(mealType=mealData['mealType'], dietary_restrictions=userData.restrictions), "Hello", 0.8, userData, None) 
      mealData['ingredients_desired'] = generated_ingredients.answer.split(", ")

    try :

      restrict = True
      found = False
      tentative = 0

      while not found and tentative < 2:
        payload = {
            "user_id": userData.id,
            "preferences": userData.restrictions + mealData['ingredients_desired'],
            "soft_restrictions": mealData['ingredients_not_desired'] + userData.disliked_ingredients,
            "hard_restrictions": hard_restrictions,
            "meal_time": mealData['mealType'],
            "previous_recommendations": previous_recommendations,
            "recommendation_count": 1,
            "diversity_factor": 0.5,
            "restrict_preference_graph": restrict, 
            "conversation_id": userData.id
        }
        
        print("\n...............................................................................")
        print(f"\nCalling /recommend with payload:\n{payload}")

        # CHIAMATA EFFETIVA (quando l'api funzionerà)
        response = requests.post(URL_RECCOMENDATION, headers=HEADER, json=payload)
        response_json = response.json()
        tentative += 1
        
        #print(f"\nStatus Code: {response.status_code}")
        print("Response JSON:", response_json)

        # estrazione prima ricetta suggerita e popolamento oggetto Recipe
        if response_json["recommendations"]== []:
           print("Nessuna raccomandazione trovata! Provo a rilassare le restrizioni...")
           restrict = False
        else:
          found = True
          
          
      if not found:
        print("Nessuna raccomandazione trovata!")
        return None, None
         
      first_recipe_reccomended_dict = response_json["recommendations"][0]

      ing_sus_info = [] # lista di IngredientApi
      for ing in first_recipe_reccomended_dict["food_info"]["ingredients"]["ingredients"]:
        ing_info = get_only_ingredient_food_info(ing) # solo il nome
        # se restituisce None ha trovato una ricetta non un ingrediente...
        if ing_info!=None:
          ing_info.display()
          ing_sus_info.append(ing_info)

      first_recipe_reccomended = rp.RecipeApi("", "", [], "", "", {}, "")
      first_recipe_reccomended.from_recommendation_dict(first_recipe_reccomended_dict)

      print("\n...............................................................................")

      return first_recipe_reccomended, ing_sus_info

    except requests.exceptions.RequestException as e:
        print(f"Errore durante la richiesta di raccomandazione all'utente {userData.id}:", e)
        return None, None

def get_alternative(recipe_name, num_alternative=5, improving_factor="overall"):
    """
    Recupera ricette alternative a una ricetta base di nome dato (POST API /alternative).
    Infine restituisce la migliore in base al fattore specificato : sostenibilità, salute o in gernerale.

    Args:
    - recipe_name : Nome della ricetta base.
    - num_alternative : Numero massimo di alternative da considerare. Default 5.
    - improving_factor : Fattore su cui migliorare ("healthiness", "sustainability", "overall").

    Returns:

    Se viene trovata almeno una ricetta migliore : 
    - base_recipe : ricetta base estratta a partire dal nome fornito, istanza della classe RecipeApi
    - base_ing_info : lista di ingredienti, istanze della classe IngredientApi, della ricetta base (per estrarre la sostenibilità e salubrità di ogni ingrediente)
    - imp_recipe : ricetta migliorata in base al fattore specificato, istanza della classe RecipeApi
    - imp_ing_info : lista di ingredienti, istanze della classe IngredientApi, della ricetta migliorata (per estrarre la sostenibilità e salubrità di ogni ingrediente)

    Altrimenti (None, None, None, None).
    """
    try :

      
      payload = {
            "food_item": recipe_name,
            "food_item_type": "recipe",
            "num_alternatives": num_alternative
      }

      print("\n...............................................................................")
      print(f"\nCalling /alternative with payload:\n{payload}")

      response = requests.post(URL_ALTERNATIVE, headers=HEADER, json=payload)
      response_json = response.json()

      print(f"\nStatus Code: {response.status_code}")
      print("Response JSON:", response_json)
      if response.status_code==404:
         return None, None, None, None

      # ricetta base che ha fatto il match
      base_recipe_dict = response_json["matched_food_item"]

      base_recipe = rp.RecipeApi("", "", [], None, None, {}, "")
      base_recipe.from_alternative_dict(base_recipe_dict)
      #base_recipe.display()

      if improving_factor=="overall":
         # estrae semplicemente la prima suggerita
        imp_recipe_dict = response_json["alternatives"][0]

        imp_recipe = rp.RecipeApi("", "", [], None, None, {}, "")
        imp_recipe.from_alternative_dict(imp_recipe_dict)
        #imp_recipe.display()

        # per stampare entrambi gli score di entrambe le ricette
        base_healthiness_score = base_recipe_dict.get("healthiness", {}).get("score", "E")
        base_sustainability_score = base_recipe_dict.get("sustainability", {}).get("score", "E")
        print(f"\nbase recipe healthiness score: {base_healthiness_score}")
        print(f"base recipe sustainability score: {base_sustainability_score}")

        imp_healthiness_score = imp_recipe_dict.get("healthiness", {}).get("score", "E")
        imp_sustainability_score = imp_recipe_dict.get("sustainability", {}).get("score", "E")
        print(f"\nimp recipe healthiness score: {imp_healthiness_score}")
        print(f"imp recipe sustainability score: {imp_sustainability_score}")

      else :
        
        # estrae la ricetta con miglior score di improving_factor rispetto a quello della ricetta che ha matchato
        base_score = base_recipe_dict.get(improving_factor, {}).get("score", "E")
        print(f"\nbase recipe {improving_factor} score: {base_score}")

        # ordina le alternative dalla migliore alla peggiore
        sorted_alts = sorted(
             response_json["alternatives"],
             key=lambda alt: alt.get(improving_factor, {}).get("score", "E")
        )

        # trova la prima alternativa che ha score < base_score (cioè migliore)
        imp_recipe_dict = None
        for alt in sorted_alts:
            # recupero score ricetta temporanea
            alt_score = alt.get(improving_factor, {}).get("score", "E")
            if alt_score < base_score: 
                imp_recipe_dict = alt
                break

        # se nessuna alternativa è migliore, prendi la prima comunque
        if imp_recipe_dict is None:
             imp_recipe_dict = response_json["alternatives"][0]

        imp_recipe = rp.RecipeApi("", "", [], None, None, {}, "")
        imp_recipe.from_alternative_dict(imp_recipe_dict)
        imp_score = imp_recipe_dict.get(improving_factor, {}).get("score", "E")
        print(f"improved recipe {improving_factor} score: {imp_score}")

      # recupero le info degli ingredienti di entrambe le ricette tramite /food info
      print("###############################################################################")

      base_ing_info = [] # lista di Ingredient
      print("base ingredients : ",base_recipe.ingredients)

      for ing in base_recipe.ingredients:
        ing_info = get_only_ingredient_food_info(ing[0]) # solo il nome
        # se restituisce None ha trovato una ricetta non un ingrediente...
        if ing_info!=None:
          ing_info.display()
          base_ing_info.append(ing_info)

      imp_ing_info = []
      print("\nimproved ingredients : ",imp_recipe.ingredients)

      for ing in imp_recipe.ingredients:
        ing_info = get_only_ingredient_food_info(ing[0]) # solo il nome
        # se restituisce None ha trovato una ricetta non un ingrediente...
        if ing_info!=None:
          ing_info.display()
          imp_ing_info.append(ing_info)

      print("###############################################################################")

      print("\n...............................................................................")
      return base_recipe, base_ing_info, imp_recipe, imp_ing_info
      
    
    except requests.exceptions.RequestException as e:
        print(f"Errore durante la richiesta di alternative {recipe_name} :", e)
        return None

def get_food_info(item, type_item):
    """
    Recupera le informazioni nutrizionali (GET API /food-info/{item}), di sostenibilità e salubrità su un alimento (ricetta o ingrediente).
    Il tipo di istanza da restituire viene interpretato in base al tipo di alimento della risposta.

    Args:
    - item : Nome dell'ingrediente o ricetta da cercare.
    - type_item : Tipo dell'elemento da cercare ("ingredient" o "recipe").

    Returns:
    - RecipeApi or IngredientApi or None: Oggetto informativo sull'alimento, oppure None in caso di errore o non trovato.
    """
    try :
      print("\n...............................................................................")
      print(f"\nCalling {URL_INFORMATION + item + '?food_item_type=' + type_item}")

      response = requests.get(URL_INFORMATION + item + '?food_item_type=' + type_item, headers=HEADER)
      response_json = response.json()
      
      print(f"\nStatus Code: {response.status_code}")
      print("Response JSON:", response_json)

      # se il codice è 404 non ha trovato nessun risultato
      if response.status_code==404:
         print("Non trovato!")
         return None
      
      # l'endpoint è lo stesso per ricette e ingredienti, ma cambia il campo food_item_type della riposta
      if response_json["food_item_type"]=="recipe":
          recipe_information = rp.RecipeApi("", "", [], None, None, {}, "")
          recipe_information.from_foodinfo_dict(response_json)
          print("\n...............................................................................")
          return recipe_information

      else:
          ingredient_information = ig.IngredientApi("", [], None, None, {}, "")
          ingredient_information.from_food_info_dict(response_json)
          print("\n...............................................................................")
          return ingredient_information
      
    except requests.exceptions.RequestException as e:
        print(f"Errore durante la richiesta di recupero informazioni {item} :", e)
        return None
   
def get_only_ingredient_food_info(item):
   """
    Recupera informazioni solo se l'item richiesto è un ingrediente (e non una ricetta).
    Utile a filtrare solo ingredienti dal database alimentare.

    Args:
    - item : Nome dell'ingrediente da cercare.

    Returns:
    - IngredientApi or None: Oggetto IngredientApi se trovato, oppure None in caso di errore o non trovato.
    """
   try :
      print("\n...............................................................................")
      print(f"\nCalling {URL_INFORMATION + item}")

      response = requests.get(URL_INFORMATION + item + '?food_item_type=ingredient', headers=HEADER)
      response_json = response.json()

      print(f"\nStatus Code: {response.status_code}")
      if response.status_code==404:
         print("Non trovato!")
         return None

      print("Response JSON:", response_json)
      
      # l'endpoint è lo stesso per ricette e ingredienti, ma cambia il campo food_item_type della riposta
      if response_json["food_item_type"]=="ingredient":
          ingredient_information = ig.IngredientApi("", [], None, None, {}, "")
          ingredient_information.from_food_info_dict(response_json)
          print("\n...............................................................................")
          return ingredient_information

      else:
          # ha trovato una ricetta...
          return None
        
   except requests.exceptions.RequestException as e:
        print(f"Errore durante la richiesta di recupero informazioni {item} :", e)
        return None
   