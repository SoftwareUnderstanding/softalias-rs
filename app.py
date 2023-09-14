import streamlit as st
from annotated_text import annotated_text
import nltk
import spacy
from spacy.matcher import Matcher
from spacy.tokenizer import Tokenizer
from spacy.util import compile_prefix_regex, compile_suffix_regex, compile_infix_regex
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

def getWikidata(entity):
    sparqlwd = SPARQLWrapper("https://query.wikidata.org/sparql", agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")

    sparqlwd.setReturnFormat(JSON)

    query=f"""
            select distinct ?software ?url ?repo where {{
            ?software wdt:P31/wdt:P279* wd:Q7397;
                    rdfs:label "{entity}"@en.
            
            OPTIONAL {{?software wdt:P1324 ?repo}}.
            OPTIONAL {{?software wdt:P856 ?url}}
  
  
            }}
            """
    
    print("Q:"+query)
    sparqlwd.setQuery(query)
   
    results = sparqlwd.query().convert()
    print("***********************")
    print(results)
    print("***********************")

    return results

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
            ?al schema:name ?a.
            optional{{?al <https://w3id.org/softalias/number_of_repetitions> ?r .}}
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
            ?group <https://w3id.org/softalias/alias> ?al .
            ?al schema:name ?a.
            optional{{?al <https://w3id.org/softalias/number_of_repetitions> ?r .}}
            filter(?a != ?alias)
            }} order by desc(?r)
            """
    
    sparqlwd.setQuery(query)
   
    results = sparqlwd.query().convert()
    print("***********************")
    print("Entity:"+str(entity))
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
    #relevance_values = [int(relevance["r"]["value"]) for relevance in relevance_list["results"]["bindings"]]
    relevance_values = [relevance["r"]["value"] if "r" in relevance else "unkown" for relevance in relevance_list["results"]["bindings"]]

    print("----------------------")
    print(relevance_names)
    print(relevance_values)

    source = pd.DataFrame({
        "Relevance": relevance_values,
        "Aliases": relevance_names
    })

   
    st.bar_chart(source.set_index("Aliases"))

def a_text(text, predictions):
    annotated_results = []
    res = [token["software-name"]["rawForm"] for token in predictions["mentions"]]
    print("TRES:"+str(res))
    last_end = 0
    for token in predictions["mentions"]:
        ent_text = token["software-name"]["rawForm"]
        ent_label = "software"
        start = token["software-name"]["offsetStart"]
        end = token["software-name"]["offsetEnd"]
        if start > last_end:
            annotated_results.append(text[last_end:start])
        annotated_results.append((ent_text, ent_label))
        last_end = end
    annotated_results.append(text[last_end:])
    annotated_text(*annotated_results)

    return res

def annotate_text(text, predictions):
    nlp = spacy.load('en_core_web_sm')

    docx = nlp(text)

    tokens = [token.text+" " for token in docx]
    print("T:"+str(tokens))

    res = []
    annotated_tokens=[]

    for token in docx:
        entity = getEntityToken(token, predictions)
        if entity != "":
            res.append((token.text+" ",entity))
            annotated_tokens.append(token.text)
        else:
            res.append(token.text+" ")

    annotated_text(res)
    return annotated_tokens

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

def remove_substrings(lista):
    lista_filtrada = []

    for elemento in lista:
        es_subcadena = False

        for otro_elemento in lista:
            if elemento != otro_elemento and elemento in otro_elemento:
                es_subcadena = True
                break

        if not es_subcadena:
            lista_filtrada.append(elemento)

    return lista_filtrada

def remove_duplicates(list_alias):
    alias_name=[]
    res={'head':{'vars':['a','r']}, 'results':{'bindings':[]}}
    for alias_element in list_alias["results"]["bindings"]:
        print(alias_element)
        print(alias_name)
        if alias_element["a"]["value"] not in alias_name:
            alias_name.append(alias_element["a"]["value"])
            res["results"]["bindings"].append(alias_element)
        print(alias_name)
    return res
    
def print_tables(entity):

    st.markdown("**Information from KG**")

    col_aliases, col_url = st.columns(2)

    with col_aliases:
        aliases_list = getRelevance(entity)

        print("Duplicates")
        print(aliases_list)

        aliases_list = remove_duplicates (aliases_list)
        print(aliases_list)

        unique_aliases = [relevance["r"]["value"] if "r" in relevance  else "unknown" for relevance in aliases_list["results"]["bindings"]]

        df_aliases = pd.DataFrame({
            "alias": [alias["a"]["value"] for alias in aliases_list["results"]["bindings"]],
            "relevance": unique_aliases
            #"relevance": [alias["r"]["value"] for alias in aliases_list["results"]["bindings"]]
        })
    
        if df_aliases.size > 0:
        
            st.data_editor(
                df_aliases,
                key = "key-alias-"+entity, 
                column_config={
                    "alias" : st.column_config.Column(
                        "Aliases",
                        help="Aliases of the entities detected",
                        width="medium"
                    ),
                    "relevance" : st.column_config.Column(
                        "# mentions",
                        help="number of mentions",
                        width="medium"
                    ),
                },
                hide_index=True
            )
        else:
            st.text("No aliases detected")

    with col_url:
        url_list = getURLs(entity)

        url_list = [entity["url"]["value"] for entity in url_list["results"]["bindings"]]

        url_list = remove_substrings(url_list)
        

        df_urls = pd.DataFrame({
            "urls": url_list,
        })
        
        if df_urls.size > 0:
            
            st.data_editor(
                df_urls,
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

    print ("******************INIT********************************************")
    st.set_page_config(page_title='softalias-demo')

    st.title("Softalias reconciliation demo")

    text_container = st.container()

    text_container.markdown("This demo combines [SoftCite](http://dx.doi.org/10.1145/3459637.3481936), a named entity recognition model for software mentions, with  Softalias-KG, a Knowledge Graph of software aliases extracted from the [biomedical literature](http://dx.doi.org/10.5061/DRYAD.6WWPZGN2C) and [Wikidata](https://dl.acm.org/doi/fullHtml/10.1145/2629489) to reconcile tool mentions found in text. "+
"To try the demo, please enter your own text in the box below (or click on the examples below to see sample text snippets) and then click on \"Analyze\". Candidate software mentions detected by [Softcite (v0.7.1)](https://github.com/softcite/software-mentions) will be highlighted in yellow, and additional aliases and tool information from the KG will be shown in tables below.")

    button_container = st.container()

    col1,col2,col3,col4 = button_container.columns(4) 

    if col1.button("Example 1"):
            st.session_state.sentence_text = "Although interactive Web-based and stand-alone methods exist for computing the Sobel test, SPSS and SAS programs that automatically run the required regression analyses and computations increase the accessibility of mediation modeling to nursing researchers."
    if col2.button("Example 2"):
            st.session_state.sentence_text = "In Python, Sklearn is the most usable and robust machine learning package. It uses a Python consistency interface to give a set of fast tools for machine learning and statistical modelling, such as classification, regression, clustering, and dimensionality reduction. NumPy, SciPy, and Matplotlib are the foundations of this package, which is mostly written in Python."
    if col3.button("Example 3"):
            st.session_state.sentence_text = "KGTK is a Python library for easy manipulation with knowledge graphs. It provides a flexible framework that allows chaining of common graph operations, such as: extraction of subgraphs, filtering, computation of graph metrics, validation, cleaning, generating embeddings, and so on. Its principal format is TSV, though we do support a number of other inputs."
    if col4.button("Example 4"):
            st.session_state.sentence_text = "This is an example about non-software entities." \
                "Barack Obama was the president of the United States from 2009 to 2017. A member of the Democratic Party, Obama was the first African-American president of the United States. He previously served as a U.S. senator from Illinois from 2005 to 2008 and as an Illinois state senator from 1997 to 2004, and previously worked as a civil rights lawyer before entering politics."

    button_container.markdown('</div>', unsafe_allow_html=True)
    
    text = st.text_area("Enter your text","Type here (longer sentences are recommended so the model can pick up the right context)", key="sentence_text")

    if st.button("Analyze"):
        nlp_results = extract_software(text)
        print ("Entities Original:"+str(nlp_results))
        
        entity_list = a_text(text,nlp_results)

        entity_list = sorted(list(set(entity_list)))
        print ("Entities:"+str(entity_list))
        
        for nlp_result in entity_list:
            st.subheader(nlp_result)
            print_tables(nlp_result)


        st.success("Done")

    st.markdown("---")
    col_about, col_figures = st.columns([2,1])
    col_about.markdown("Daniel Garijo, Hector Lopez and Esteban Gonzalez")
    col_about.markdown("Version: 0.0.1")
    col_about.markdown("Last revision: September, 2023")
    col_about.markdown("Github: <https://github.com/SoftwareUnderstanding/softalias-rs>")
    col_about.markdown("Built with [streamlit](https://streamlit.io/)")

    logo_oeg, logo_upm = col_figures.columns(2)
    
    logo_oeg.image("images/logo-oeg.gif", width=100)
    logo_upm.image("images/upmlogo.png", width=100)
    hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

if __name__ == '__main__':
    main()

