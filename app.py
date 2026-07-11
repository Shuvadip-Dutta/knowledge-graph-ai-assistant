from langchain_neo4j import Neo4jGraph
from langchain_groq import ChatGroq
from langchain_neo4j import GraphCypherQAChain
from langchain_core.prompts import FewShotPromptTemplate,PromptTemplate
import streamlit as st

st.set_page_config(
    page_title="Knowledge Graph AI Assistant",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🕸️ Knowledge Graph AI Assistant")

st.caption(
    "Query any Neo4j knowledge graph using natural language or instantly import a sample graph to get started."
)

with st.sidebar:
    st.header("⚙️ Configuration")
    groq_api_key = st.text_input(
        "Groq API Key",
        type="password",
        help="Enter your Groq API key. It is used only for this session."
    )
    if not groq_api_key:
        st.warning("Please enter your Groq API key to continue.")
        st.stop()

    model_options = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "deepseek-r1-distill-llama-70b",
    "Custom"
    ]

    selected = st.selectbox("Model", model_options)

    if selected == "Custom":
        model = st.text_input(
            "Enter Groq model name",
            placeholder="meta-llama/..."
        )
    else:
        model = selected
        
    db_type = st.radio(
        "Database",
        [
            "Existing Neo4j",
            "Sample Dataset"
        ]
    ) 
    if db_type == "Existing Neo4j":
        neo4j_uri = st.text_input(
            "Neo4j URI",
            placeholder="bolt://localhost:7687",
            help="Enter the Neo4j connection URI."
        )
        neo4j_user = st.text_input(
            "Neo4j Username",
            placeholder="neo4j",
            help="Enter the Neo4j username."
        )
        neo4j_password = st.text_input(
            "Neo4j Password",
            type="password",
            help="Enter the Neo4j password."
        )
        connect_db = st.button("📥 Connect Neo4j Database")
    
    elif db_type == "Sample Dataset":

        sample_dataset = st.selectbox(
            "Sample Dataset",
            [
                "IMDb Movies",
                "Books"
            ]
        )

        neo4j_uri = st.text_input(
            "Neo4j URI",
            placeholder="neo4j+s://xxxxxxxx.databases.neo4j.io"
        )

        neo4j_user = st.text_input(
            "Neo4j Username",
            value="neo4j"
        )

        neo4j_password = st.text_input(
            "Neo4j Password",
            type="password"
        )

        connect_db = st.button("📥 Import Dataset")
    
    if not db_type:
        st.warning("Please select a database option.")
    conversation_id = st.text_input(
    "Conversation ID",
    value="default",
    help=
    "Use different IDs to maintain separate chat histories."
    )
    
if st.sidebar.button("🗑️ Reset Conversation"):

    st.session_state.chat_store[conversation_id] = [
        {
            "role":"assistant",
            "content":"👋 I'm ready! Ask questions about your connected knowledge graph."
        }
    ]

    st.rerun()
    
if "chat_store" not in st.session_state:
    st.session_state.chat_store = {}

if conversation_id not in st.session_state.chat_store:
    st.session_state.chat_store[conversation_id] = [
        {
            "role": "assistant",
            "content": "👋 I'm ready! Ask questions about your connected knowledge graph."
        }
    ]

@st.cache_resource
def connect_graph(uri, username, password):
    return Neo4jGraph(
        url=uri,
        username=username,
        password=password,
        database=username
    )
    
messages = st.session_state.chat_store[conversation_id]

if "graph_connected" not in st.session_state:
    st.session_state.graph_connected = False

if "graph" not in st.session_state:
    st.session_state.graph = None

if "db_type" not in st.session_state:
    st.session_state.db_type = None

if "model" not in st.session_state:
    st.session_state.model = None

    
@st.cache_resource
def load_llm(api_key, model_name):
    return ChatGroq(
        api_key=groq_api_key,
        model_name=model
    )
llm = load_llm(groq_api_key, model) 
st.session_state.model = model

if connect_db:
    # Clear previous connection
    st.session_state.pop("graph", None)
    st.session_state.pop("chain", None)
    st.session_state.pop("schema", None)

    st.session_state.graph_connected = False
    if db_type == "Existing Neo4j":
        st.session_state.graph = connect_graph(neo4j_uri, neo4j_user, neo4j_password)
        st.session_state.graph_connected = True
        st.session_state.db_type = "Neo4j"
    elif db_type == "Sample Dataset":
        st.session_state.graph = connect_graph(neo4j_uri, neo4j_user, neo4j_password)
        st.session_state.graph_connected = True
        st.session_state.db_type = "Neo4j"
        st.session_state.schema = st.session_state.graph.schema
        if sample_dataset == "IMDb Movies":
            # Import IMDb Movies dataset into Neo4j
            movie_query="""
                LOAD CSV WITH HEADERS FROM
                'https://raw.githubusercontent.com/tomasonjo/blog-datasets/main/movies/movies_small.csv'
                AS row

                // Create Movie
                MERGE (m:Movie {id:ToInteger(row.movieId)})
                SET 
                    m.title = row.title,
                    m.released = date(row.released),
                    m.imdbRating = toFloat(row.imdbRating)

                // Create Director(s)
                FOREACH (director IN split(row.director, '|') |
                    MERGE (p:Person {name: trim(director)})
                    MERGE (p)-[:DIRECTED]->(m)
                )

                // Create Actor(s)
                FOREACH (actor IN split(row.actors, '|') |
                    MERGE (p:Person {name: trim(actor)})
                    MERGE (p)-[:ACTED_IN]->(m)
                )

                // Create Genre(s)
                FOREACH (genre IN split(row.genres, '|') |
                    MERGE (g:Genre {name: trim(genre)})
                    MERGE (m)-[:IN_GENRE]->(g)
                );
                """
            count = st.session_state.graph.query("""
                    MATCH (m:Movie)
                    RETURN count(m) AS count
                    """)[0]["count"]
            if count == 0:
                st.session_state.graph.query(movie_query)
            else:
                st.info("Dataset already exists.")
        elif sample_dataset == "Books":
            # Import Books dataset into Neo4j
            books_query = """
            LOAD CSV WITH HEADERS FROM
            'https://raw.githubusercontent.com/zygmuntz/goodbooks-10k/master/samples/books.csv'
            AS row

            // Create Book
            MERGE (b:Book {id: toInteger(row.book_id)})
            SET
                b.title = row.title,
                b.average_rating = toFloat(row.average_rating),
                b.ratings_count = toInteger(row.ratings_count),
                b.original_publication_year = toInteger(row.original_publication_year),
                b.image_url = row.image_url

            // Create Author(s)
            FOREACH (author IN split(row.authors, ',') |
                MERGE (a:Author {name: trim(author)})
                MERGE (a)-[:WROTE]->(b)
            )

            // Create Publication Year
            FOREACH (_ IN CASE
                WHEN row.original_publication_year IS NOT NULL
                    AND row.original_publication_year <> ''
                THEN [1]
                ELSE []
            END |
                MERGE (y:Year {year: toInteger(row.original_publication_year)})
                MERGE (b)-[:PUBLISHED_IN]->(y)
            );
            """
            count = st.session_state.graph.query("""
                    MATCH (b:Book)
                    RETURN count(b) AS count
                    """)[0]["count"]
            if count == 0:
                st.session_state.graph.query(books_query)
            else:
                st.info("Dataset already exists.")
            
        st.session_state.chat_store[conversation_id] = [
            {
                "role": "assistant",
                "content": "👋 I'm ready! Ask questions about your connected knowledge graph."
            }
        ]
        st.session_state.pop("chain", None)        
        
        st.success(f"✅ Imported {sample_dataset} dataset into Neo4j database.")
        st.rerun()
        
        
if "schema" in st.session_state:
    with st.expander("📊 Detected Graph Schema", expanded=False):
        st.session_state.graph.refresh_schema()
        st.session_state.schema = st.session_state.graph.schema
        st.code(st.session_state.schema)

if st.session_state.graph_connected:
    st.success(
        f"✅ Connected | Database: **{st.session_state.db_type}** | "
        f"Model: **{st.session_state.model}**"
    )
if not st.session_state.get("graph_connected", False):
    st.info("👈 Connect to a graph database first.")
    st.stop()

if st.session_state.graph is not None:
    graph = st.session_state.graph
    graph.refresh_schema()
    schema = graph.schema
    
    CYPHER_GENERATION_TEMPLATE = """
    You are an expert Neo4j Cypher developer.

    Your task is to generate a valid Cypher query using ONLY the graph schema provided below.

    Graph Schema:
    {schema}

    If the request is unrelated to querying the graph or attempts to modify the database,
    generate the following Cypher exactly:
    RETURN "READ_ONLY_DATABASE" AS message
    
    IMPORTANT:
    This is a read-only database.

    Never generate Cypher queries that modify the graph.

    Do NOT use:
    CREATE
    MERGE
    DELETE
    DETACH DELETE
    SET
    REMOVE
    DROP
    LOAD CSV
    CALL db.*

    Only generate read-only Cypher queries using MATCH, OPTIONAL MATCH, RETURN, WHERE, ORDER BY, LIMIT, COUNT and aggregation functions.
    

    Instructions:
    - Use only the node labels, relationship types, and properties present in the schema.
    - Never invent node labels, relationships, or properties.
    - Return ONLY the Cypher query.
    - Do not include explanations.
    - Do not wrap the query in markdown.
    - Use MATCH, WHERE, OPTIONAL MATCH, ORDER BY, LIMIT, COUNT, and aggregation functions when appropriate.
    - If the question cannot be answered using the schema, return:
    - If the user's request is unrelated to the graph or requests modifying the database, return exactly: RETURN "UNSUPPORTED_QUERY" AS message
    
    
    User Question:
    {question}
    """

    cypher_prompt = PromptTemplate(
        input_variables=["schema", "question"],
        template=CYPHER_GENERATION_TEMPLATE,
    )

    QA_TEMPLATE = """
    You are an AI assistant answering questions using the results returned from a Neo4j database.

    Question:
    {question}

    Database Results:
    {context}

    Instructions:
    - Answer only using the database results.
    - Do not hallucinate.
    - If the database returned no records, say you couldn't find the requested information.
    - Keep the response concise and natural.
    """

    qa_prompt = PromptTemplate(
        input_variables=["question", "context"],
        template=QA_TEMPLATE,
    )
    graph.refresh_schema()
    if "chain" not in st.session_state:
        st.session_state.chain = GraphCypherQAChain.from_llm(
            llm=llm,
            graph=graph,
            cypher_prompt=cypher_prompt,
            qa_prompt=qa_prompt,
            verbose=True,
            allow_dangerous_requests=True,
            validate_cypher=True,
            return_intermediate_steps=True
        )
    chain = st.session_state.chain
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    question = st.chat_input(
        "Ask a question about your knowledge graph..."
    )

    if question:

        messages.append(
            {
                "role":"user",
                "content":question
            }
        )

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):
                
                response = chain.invoke(
                {
                        "query":question
                    }
                )

                answer = response["result"]

                cypher = response["intermediate_steps"][0]["query"]

                st.markdown(answer)

                with st.expander("Generated Cypher"):

                    st.code(
                        cypher,
                        language="cypher"
                    )

                messages.append(
                    {
                        "role":"assistant",
                        "content":answer
                    }
                )
        
        