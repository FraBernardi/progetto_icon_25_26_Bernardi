import pandas as pd
import os
from owlready2 import *

def populate_ontology():
    print("[INFO] Caricamento ontologia vuota...")
    onto_path = os.path.join(os.path.dirname(__file__), '..', 'ontology', 'theoffice_empty.rdf')
    onto = get_ontology(onto_path).load()

    print("[INFO] Lettura del dataset the_office_series.csv...")
    dataset_path = os.path.join(os.path.dirname(__file__), '..', 'dataset', 'the_office_series.csv')
    df = pd.read_csv(dataset_path)

    with onto:
        # --- 1. CREAZIONE INDIVIDUI SEMANTICI (TBox -> ABox) ---
        dundie = onto.Premio_Dundie("I_Dundies")
        festa = onto.Festa_in_Ufficio("Festa_Aziendale")
        matrimonio = onto.Matrimonio("Matrimonio_Jim_e_Pam")
        addio = onto.Addio_Personaggio("Addio_Michael_Scott")
        assenza_michael = onto.Assenza_di_Michael("Mancanza_Michael")

        print("[INFO] Popolamento degli episodi...")
        # --- 2. CREAZIONE EPISODI E COLLEGAMENTI ---
        for index, row in df.iterrows():
            
            ep_id = f"Episode_{index}"
            episodio = onto.Episodio(ep_id)

            about_text = str(row['About']).lower() if pd.notna(row['About']) else ""
            title_text = str(row['EpisodeTitle']).lower() if pd.notna(row['EpisodeTitle']) else ""

            if "dundie" in about_text or "dundie" in title_text:
                episodio.haOggetto.append(dundie)

            if "party" in about_text or "christmas" in about_text or "birthday" in about_text:
                episodio.haEvento.append(festa)

            if "wedding" in about_text or "niagara" in title_text or "marriage" in about_text:
                episodio.haEvento.append(matrimonio)

            if "goodbye, michael" in title_text or "goodbye michael" in title_text:
                episodio.haEvento.append(addio)

            if 'Season' in row and pd.notna(row['Season']) and int(row['Season']) >= 8:
                episodio.haElementoNarrativo.append(assenza_michael)

            if 'GuestStars' in row and pd.notna(row['GuestStars']):
                nome_guest = str(row['GuestStars']).replace(' ', '_').replace(',', '')
                guest = onto.Guest_star(f"Guest_{nome_guest}_{index}")
                episodio.haPersonaggio.append(guest)

    # --- 3. SALVATAGGIO ONTOLOGIA POPOLATA ---
    populated_onto_path = os.path.join(os.path.dirname(__file__), '..', 'ontology', 'theoffice_populated.rdf')
    onto.save(file=populated_onto_path, format="rdfxml")
    print(f"[INFO] Ontologia popolata salvata in: {populated_onto_path}")

def run_reasoning():
    print("[INFO] Caricamento ontologia per il ragionamento logico...")
    populated_onto_path = os.path.join(os.path.dirname(__file__), '..', 'ontology', 'theoffice_populated.rdf')
    onto = get_ontology(populated_onto_path).load()

    with onto:
        print("[INFO] Avvio del motore HermiT. Attendi...")
        sync_reasoner()
        print("[INFO] Ragionamento concluso!")

    results = {}
    for ep in onto.Episodio.instances():
        if ep in onto.Episodio_eccellente.instances():
            results[ep.name] = 'Eccellente'
        elif ep in onto.Episodio_scarso.instances():
            results[ep.name] = 'Scarso'
        else:
            results[ep.name] = 'Buono'

    return results