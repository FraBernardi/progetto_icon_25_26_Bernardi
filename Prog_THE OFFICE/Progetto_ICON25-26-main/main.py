import pandas as pd
import os
from src import learning
from src import reasoning
from sklearn.preprocessing import LabelEncoder

def main():
    print("AVVIO PROGETTO: ")
    dataset_path = os.path.join(os.path.dirname(__file__), 'dataset', 'the_office_series.csv')

    print("\n1° parte: esecuzione modelli sul dataset originale...")

    dataset_originale = learning.load_dataset(dataset_path)
    X_orig, y_orig = learning.preprocessing_dataset(dataset_originale.copy())

    print("\nAddestramento e valutazione del Decision Tree...")
    dt_model_orig = learning.decisiontree_classifier(X_orig, y_orig)

    print("\nAddestramento e valutazione del Random Forest...")
    rf_model_orig = learning.randomforest_classifier(X_orig, y_orig)

    print("\n1° parte completata.")

    print("\n2° parte: esecuzione ragionamento automatico...")

    populated_onto_path = os.path.join(os.path.dirname(__file__), 'ontology', 'theoffice_populated.rdf')
    if not os.path.exists(populated_onto_path):
        print("[INFO] Ontologia popolata non trovata. Avvio il processo di popolamento...")
        reasoning.populate_ontology()
        print("[INFO] Popolamento completato.")
    else:
        print("[INFO] Utilizzo dell'ontologia popolata esistente.")
        
    print("[INFO] Avvio del ragionatore semantico per classificare gli episodi...")
    semantic_results = reasoning.run_reasoning()
    
    semantic_df = pd.DataFrame(list(semantic_results.items()), columns=['Episode_ID', 'Semantic_Class'])
      # --- INIZIO DIAGNOSTICA ---
    print("\n--- DIAGNOSTICA REASONER ---")
    print(semantic_df['Semantic_Class'].value_counts())
    print("----------------------------\n")
    # --- FINE DIAGNOSTICA ---
    
    print("\nDataset arricchito con la nuova feature 'Semantic_Class'.")
    print("\n2° parte completata.")

    print("\n3° parte: esecuzione dei modelli su dataset arricchito con conoscenza di fondo...")
    
    X_arr = X_orig.copy()
    
    # Generiamo lo stesso ID basato sull'indice
    X_arr['Episode_ID'] = [f"Episode_{i}" for i in dataset_originale.index]
    
    X_arr = pd.merge(X_arr, semantic_df, on='Episode_ID', how='left')
    X_arr = X_arr.drop(columns=['Episode_ID'])

    # ---> RIGA COMMENTATA: RIPRISTINIAMO IL SISTEMA IBRIDO (Ontologia + Statistica) <---
    # X_arr = X_arr.drop(columns=['Votes', 'Viewership', 'Viewers'], errors='ignore')
    # --------------------------------------------------------------------------

    X_arr['Semantic_Class'] = X_arr['Semantic_Class'].fillna('Non Annotato')
    
    le = LabelEncoder()
    X_arr['Semantic_Class'] = le.fit_transform(X_arr['Semantic_Class'])
    
    y_arr = y_orig.copy()

    print("\nAddestramento e valutazione del Decision Tree (con BK)...")
    dt_model_arr = learning.decisiontree_classifier(X_arr, y_arr)

    print("\nAddestramento e valutazione del Random Forest (con BK)...")
    rf_model_arr = learning.randomforest_classifier(X_arr, y_arr)

    print("\n3° parte completata. Esperimento concluso.")

if __name__ == "__main__":
    main()