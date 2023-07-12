import streamlit as st
from annotated_text import annotated_text
import nltk
import spacy
import requests
import json
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON


def extract_software(message):

    url = 'https://cloud.science-miner.com/software/service/processSoftwareText'
    url = 'https://thesis.esteban.linkeddata.es/service/processSoftwareText'
    
    payload = {"text":message}
    results = requests.post(url, data=payload)

    print(results.text)

    return results.json()

def getURLs(entity):
    sparqlwd = SPARQLWrapper("https://softalias.linkeddata.es/softalias/", agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")

    sparqlwd.setReturnFormat(JSON)

    query=f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX schema: <https://schema.org/>
            SELECT distinct ?url  WHERE {{
            ?group <https://w3id.org/softalias/alias> ?alias .
            ?alias schema:name '{entity}' .
            ?group schema:url ?url .
            ?group <https://w3id.org/softalias/alias>?al . 
            ?al schema:name ?a;
                <https://w3id.org/softalias/number_of_repetitions> ?r .
            filter(?a != ?alias)
                
            }} LIMIT 100
            """
    
    sparqlwd.setQuery(query)
   
    results = sparqlwd.query().convert()
    print("***********************")
    print(results)
    print("***********************")

    return results

def getRelevance(entity):
    sparqlwd = SPARQLWrapper("https://softalias.linkeddata.es/softalias/", agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")

    sparqlwd.setReturnFormat(JSON)

    query=f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX schema: <https://schema.org/>
            SELECT distinct ?a ?r WHERE {{
            ?group <https://w3id.org/softalias/alias> ?alias .
            ?alias schema:name '{entity}' .
            ?group schema:url ?url .
            ?group <https://w3id.org/softalias/alias>?al . 
            ?al schema:name ?a;
                <https://w3id.org/softalias/number_of_repetitions> ?r .
            filter(?a != ?alias)
                
            }}
            """
    
    sparqlwd.setQuery(query)
   
    results = sparqlwd.query().convert()
    print("***********************")
    print(results)
    print("***********************")

    return results

def getAliases(entity):

    sparqlwd = SPARQLWrapper("https://softalias.linkeddata.es/softalias/", agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")

    sparqlwd.setReturnFormat(JSON)

    query=f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX schema: <https://schema.org/>
            SELECT distinct ?a ?group  WHERE {{
            ?group <https://w3id.org/softalias/alias> ?alias .
            ?alias schema:name '{entity}' .
            ?group schema:url ?url .
            ?group <https://w3id.org/softalias/alias>?al . 
            ?al schema:name ?a;
                <https://w3id.org/softalias/number_of_repetitions> ?r .
            filter(?a != ?alias)
                
            }} 
            """
    
    sparqlwd.setQuery(query)
   
    results = sparqlwd.query().convert()
    print("***********************")
    print(results)
    print("***********************")

    return results

def getEntityToken(token, predictions):

    
    for prediction in predictions["mentions"]:
        if token.idx == prediction["software-name"]["offsetStart"]:
            return "software"
    
    return ""

def print_chart(entity):

    relevance_list = getRelevance(entity)

    relevance_names = [relevance["a"]["value"] for relevance in relevance_list["results"]["bindings"]]
    relevance_values = [int(relevance["r"]["value"]) for relevance in relevance_list["results"]["bindings"]]

    print("----------------------")
    print(relevance_names)
    print(relevance_values)

    source = pd.DataFrame({
        "Relevance": relevance_values,
        "Aliases": relevance_names
    })

   
    st.bar_chart(source.set_index("Aliases"))

def annotate_text(text, predictions):
    nlp = spacy.load('en_core_web_sm')
    docx = nlp(text)

    tokens = [token.text+" " for token in docx]

    res = []

    for token in docx:
        entity = getEntityToken(token, predictions)
        if entity != "":
            res.append((token.text+" ",entity))
        else:
            res.append(token.text+" ")

    annotated_text(res)

def getMaxRelation(relations):
    name = "none"
    score = -1
    print("RElations:"+str(relations))
    for relation in relations:
        print("Relation:"+str(relation))
        if relations[relation]["value"] and relations[relation]["score"] > score:
            name = relation
            score = relations[relation]["score"]
    
    return name


def print_table(table):
    name = []
    aliases = []
    urls = []


    for software in table:
        name.append(software["software-name"]["rawForm"])

        url_list = getURLs(software["software-name"]["rawForm"])
        urls.append([entity["url"]["value"] for entity in url_list["results"]["bindings"]])
        aliases_list = getAliases(software["software-name"]["rawForm"])

        aliases.append([alias["a"]["value"] for alias in aliases_list["results"]["bindings"]])
    
    df = pd.DataFrame({
        "software":name,
        "urls": urls,
        "aliases":aliases
        })
    
    
    st.data_editor(
        df, 
        column_config={
            "name" : "Software detected",
            "url" : st.column_config.ListColumn(
                "Links"
            ),
            "aliases" : st.column_config.ListColumn(
                "Aliases"
            ),
        },
        hide_index=True
    )
    
def print_tables(entity):
    col_aliases, col_url = st.columns(2)

    with col_aliases:
        aliases_list = getRelevance(entity)

        

        df = pd.DataFrame({
            "alias": [alias["a"]["value"] for alias in aliases_list["results"]["bindings"]],
            "relevance": [alias["r"]["value"] for alias in aliases_list["results"]["bindings"]]
        })
    
        if df.size > 0:
        
            st.data_editor(
                df,
                key = "key-alias-"+entity, 
                column_config={
                    "alias" : st.column_config.Column(
                        "Aliases",
                        help="Aliases of the entities detected",
                        width="medium"
                    ),
                    "relevance" : st.column_config.Column(
                        "Relevance",
                        help="Relevance of the aliases detected",
                        width="medium"
                    ),
                },
                hide_index=True
            )
        else:
            st.text("No aliases detected")

    with col_url:
        url_list = getURLs(entity)

        

        df = pd.DataFrame({
            "urls": [entity["url"]["value"] for entity in url_list["results"]["bindings"]],
        })
        
        if df.size > 0:
            
            st.data_editor(
                df,
                key = "key-url-"+entity, 
                column_config={
                    "urls" : st.column_config.LinkColumn(
                        "Links",
                        help="Links of the concepts detected"
                    )
                },
                hide_index=True
            )
        else:
            st.text("No url detected")


def get_example():
    st.session_state.sentence_text = "Ejemplo1"

def main():
    st.title("DEMO: Aliases")

    if st.button("Example 1"):
        st.session_state.sentence_text = "I use spss to analyze my results. This software is equivalent to SpSS."

    if st.button("Example 2"):
        st.session_state.sentence_text = "The use of Microsoft Excel is not indicated to analyze data. It is better to use some python package such as pandas."

    
    st.subheader("Add the text to process")
    text = st.text_area("Enter your text","Type here", key="sentence_text")

    if st.button("Analyze"):
        nlp_results = extract_software(text)
        print(nlp_results["mentions"])
        
        annotate_text(text,nlp_results)

        entity_list = [x["software-name"]["rawForm"] for x in nlp_results["mentions"]]
        entity_list = [x for x in entity_list if entity_list.count(x) == 1]
      
        
        for nlp_result in entity_list:
            st.subheader(nlp_result)
            print_tables(nlp_result)
        #print_table(nlp_result["mentions"])
        #print_chart("spss")

        st.success("Done")


if __name__ == '__main__':
    main()

