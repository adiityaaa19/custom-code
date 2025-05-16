from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage
from simple_salesforce import Salesforce
import re
import requests
from langchain.callbacks.manager import CallbackManager
from langchain_core.output_parsers import StrOutputParser
import traceback
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv
import logging
from langchain_openai import AzureChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
import asyncio
 

mcp=FastMCP(
    name="tool_soql",
    port=80,
    timeout=30,
    debug=True
)
 
logger = logging.getLogger(__name__)
 
load_dotenv()
chat_history = []
import os
class SalesforceHandler:
 
    def __init__(self):
        self.logger=logger
        self.chat_history=chat_history
        # self.llm=AzureChatOpenAI(
        #     azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT_GPT"),
        #     azure_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
        #     openai_api_type="azure",
        #     api_version=os.environ.get("AZURE_OPENAI_VERSION"),
        #     api_key=os.environ.get("AZURE_OPENAI_API_KEY_GPT"),
        #     temperature=0
        # )
       
        # Initialize Gemini
        genai.configure(api_key="AIzaSyBPFd-0SX9RIqdpltDCtMdhaui4i1DoFx8")
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            #model="gemini-2.5-pro-exp-03-25",
            temperature=0
        )
       
        self.sf = None
        self.schema_info = {}
       
  # Placeholder for Salesforce connection
 
 
    def authenticate(self):
        """Authenticate to Salesforce using the provided settings."""
        # print("Client ID: ",self.settings.client_id)
        data = {
            'grant_type': 'password',
            'client_id': os.getenv("salesforce_clientid"),
            'client_secret': os.getenv("salesforce_clientsecret"),
            'username': os.getenv("salesforce_username"),
            'password': os.getenv("salesforce_password")
        }
        try:
            auth_url =os.getenv("salesforce_authurl")
            response = requests.post(auth_url, data=data)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            access_token = response.json()['access_token']
            instance_url = response.json()['instance_url']
            self.sf = Salesforce(instance_url=instance_url, session_id=access_token)
            self.logger.info("Authentication successful!")
        except requests.exceptions.RequestException as e:
            self.logger.info(f"Error authenticating to Salesforce: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.info(f"Response content: {e.response.text}")
            raise  # Reraise the exception after infoging
        # sf_description = self.sf.describe()
        # with open('sf_description.txt', 'w') as file:
        #     file.write(str(sf_description))
        return self.sf
    def extract_soql_query(self,response: str):
           
        """
        Robust SQL query extraction with thorough cleaning
       
        Args:
            response (str): The response potentially containing an SQL query
       
        Returns:
            str: A clean, formatted SQL query
        """
        # Remove code block markers and excessive whitespace
        cleaned_response = response.replace('```sql', '').replace('```', '').strip()
        cleaned_response = cleaned_response.replace('\\_', '_').replace('\\*', '*')  # Remove escape characters
        # Use regex to find SQL query
        match = re.search(r'(SELECT.*?;)', cleaned_response, re.DOTALL | re.IGNORECASE | re.MULTILINE)
       
        if match:
            # Extract and clean the query
            sql_query = match.group(1)
            sql_query = re.sub(r'\s+', ' ', sql_query).strip()
           
            # Ensure semicolon at the end
            if not sql_query.endswith(';'):
                sql_query += ';'
           
            return sql_query
       
        # Fallback method
        lines = cleaned_response.split('\n')
        sql_lines = [line.strip() for line in lines if line.strip().upper().startswith('SELECT')]
       
        if sql_lines:
            sql_query = ' '.join(sql_lines)
            if not sql_query.endswith(';'):
                sql_query += ';'
            return sql_query
       
        raise ValueError("No valid SQL query found in the response")
    # def validate_soql_query(self,sql_query):
    #     required_clauses = ['SELECT', 'FROM']
    #     if not all(clause in sql_query.upper() for clause in required_clauses):
    #         raise ValueError("Generated SQL is missing required clauses.")
    #     if 'GROUP BY' in sql_query.upper() and 'COUNT' in sql_query.upper():
    #         group_by_parts = sql_query.upper().split('GROUP BY')[1].strip()
    #         if not group_by_parts:
    #             raise ValueError("GROUP BY clause is incomplete.")
    #     return True
    def run_query(self,sf:Salesforce,soql_query:str):
        try:
            result=sf.query(soql_query)
            return result
        except Exception as e:
            raise ValueError(f"Error executing query: {str(e)}")
    def get_response(self,user_query,sf:Salesforce,chat_history:list):
        """
            Generate a response based on the user's query and database context.
           
            Args:
                user_query (str): The user's input query
                sf (Salesforce): The Salesforce connection object
           
            Returns:
                Tuple[str, str, str]: Natural language response, SQL query, and HTML visualization
            """
        try:
            schema=self.get_basic_schema(sf)
            soql_chain=self.get_soql_chain(schema)
           
            soql_query_response = soql_chain.invoke({
                    "question": user_query,
                    "chat_history": chat_history,
                })
            self.logger.info(f"SOQL Query Response: {soql_query_response}")
            soql_query = self.extract_soql_query(soql_query_response)
            soql_query = soql_query.replace('\\*', '*')  # Ensure all escapes are removed
            soql_query=soql_query.replace(';', '')  # Remove semicolon
                # Validate SQL query
            # self.validate_soql_query(soql_query)
            print(f"Generated SQL Query: {soql_query}")
            # soql_query="SELECT Id, Name, Amount__c, Opportunity_Stage__c, Close_Date__c, Account__c, Contact__c FROM Your_Opportunity__c LIMIT 3"
           
            html_visualization = ""
            try:
                soql_result = self.execute_soql_query(sf,soql_query)
               
                # Generate visualization based on query and results
                visualization_config = self.generate_visualization(user_query, soql_result)
                self.logger.info(f"Generated visualization config: {visualization_config}")
               
                # Generate HTML for the visualization
                html_visualization = self.render_visualization_html(visualization_config)
               
                self.logger.info(f"Query Result: {soql_result}")
               
            except Exception as query_exec_error:
                self.logger.error(f"Query Execution Error: {query_exec_error}")
                return f"Error executing query: {query_exec_error}", soql_query, ""
           
                        # Deliver an accurate and user-friendly explanation, reflecting the data and insights derived from the SOQL query execution. Do not include introductory phrases or references to the user's question explicitly.
                                    # Deliver an accurate and user-friendly explanation, reflecting the data and insights derived from the SOQL query execution. Do not include introductory phrases or references to the user's question explicitly.
           
            response_template = """
           You are a smart answer and description generator. You perform two tasks:
 
            1. Looking at the provided User's Question and SOQL Response, generate a short answer to the User's Question based on the SOQL Response (the answer should be a in natural language and it should NOT be a description about the SOQL Response or query).
            2. After the Answer, you display the Visualization Config in JSON format.
            3. Finally Format your response as a single markdown appropriate headers and content.
 
            -DO NOT write anything by urself at all(even if the SOQL Response does not have the answer to the user's question) and also do Not write ```json```, strictly paste the JSON object.
 
            -----------------------------------------------------------------------
 
            SOQL Query: {query}
            User's Question: {question}
            SOQL Response: {response}
            Visualization Config: {visualization_config}
           
            -----------------------------------------------------------------------
            Output:
            (SOQL response summary123@): a short answer(to the "User's Question") based on the 'SOQL Response'.
            (Visualization Config321@): (a JSON object with the visualization configuration)
            """
               
            prompt = ChatPromptTemplate.from_template(response_template)
            llm=self.llm
           
            chain = (
                    RunnablePassthrough.assign(
                        response=lambda _: str(soql_result),
                    )
                    | prompt
                    | llm
                    | StrOutputParser()
                )
            natural_response = chain.invoke({
                    "question": user_query,
                    "query": soql_query,
                    "response": str(soql_result),
                    "visualization_config": str(visualization_config)
                })
            # self.logger.info(f"Natural Language Response: {natural_response}")
            # print("Natural Language Response: ",natural_response)
            return natural_response, soql_query, html_visualization
   
        except Exception as e:
                # Comprehensive error logging
                self.logger.error(f"Response Generation Error: {e}")
                self.logger.error(f"Detailed Error: {traceback.format_exc()}")
                return f"Error processing your query: {e}", "", ""
 
    def get_basic_schema(self,sf):
        try:
            if not sf:
                self.authenticate()
               
           
           
            # Get list of commonly used standard objects
            standard_objects = ['Account', 'Contact', 'Your_Opportunity__c', 'Task']
           
            for object_name in standard_objects:
                try:
                    # Get object description
                    obj_desc = getattr(sf, object_name).describe()
                   
                    # Get only essential field information
                    fields = [{
                        'name': field['name'],
                        'type': field['type']
                    } for field in obj_desc['fields']]
                   
                    self.schema_info[object_name] = {
                        'fields': fields
                    }
                   
                except Exception as e:
                    self.logger.error(f"Error describing {object_name}: {str(e)}")
                    continue
                   
            return self.schema_info
           
        except Exception as e:
            self.logger.error(f"Error fetching schema: {str(e)}")
            return {"error": str(e)}
    def execute_soql_query(self,sf, query: str):
        """
        Execute a SOQL query and return the result.
       
        :param query: The SOQL query to execute.
        :return: The result of the query.
        """
        try:
            result = sf.query(query)
            print("Result from execute_soql_query: ",result)
            return result
        except requests.exceptions.RequestException as e:
            self.logger.info(f"Error executing SOQL query: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.info(f"Response content: {e.response.text}")
            raise  # Reraise the exception after logging
   
    def get_soql_chain(self,schema):
            template = """
                 You are a proficient SOQL expert tasked with generating SOQL queries based on a provided Salesforce schema. Using the schema below, write an accurate SOQL query to address the user's question, adhering to the following rules:
 
                    Properly reference object and field names as per the schema.
                    Use correct relationships for any joins.
                    You must use the following clauses whenever necessary - SELECT, JOIN, FROM, WHERE, LIMIT, GROUP BY, ORDER BY , HAVING , DISTINCT, INCLUDES in your query.
                    Avoid ambiguity by prefixing field names with their respective object names (e.g., object.field).
                    Include necessary clauses such as GROUP BY for aggregate operations.
                    Output only the SOQL query without explanations or comments.
                    Keep in mind that SOQL is object-oriented, so you will need to reference objects and fields in your query.
 
                    Salesforce Schema: {schema}
                    Conversation History: {chat_history}
                    Question: {question}
                    SOQL Query:
                    Example Format:
                    SELECT Id, Name, Amount__c, Opportunity_Stage__c, Close_Date__c, Account__c, Contact__c FROM Your_Opportunity__c LIMIT 3
                """
            prompt = ChatPromptTemplate.from_template(template)
 
            llm =self.llm
           
 
            try:
                schema = schema  # Fetch full schema info without engine
            except Exception as e:
                self.logger.error(f"Schema fetching error: {e}")
                schema = {}  # Fallback to empty schema
 
            return (
                RunnablePassthrough.assign(schema=lambda _: schema)
                | prompt
                | llm
                | StrOutputParser()
            )
 
    def render_visualization_html(self, chart_config):
        """
        Renders the ECharts visualization configuration as HTML.
       
        Args:
            chart_config (dict): ECharts configuration in JSON format
           
        Returns:
            str: HTML string that can be embedded to display the visualization
        """
        import json
       
        # Convert the chart config to a JSON string
        chart_json = json.dumps(chart_config)
       
        # Create HTML with ECharts
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Salesforce Data Visualization</title>
            <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
        </head>
        <body>
            <div id="chart-container" style="width: 100%; height: 500px;"></div>
            <script type="text/javascript">
                var chartDom = document.getElementById('chart-container');
                var myChart = echarts.init(chartDom);
                var option = {chart_json};
               
                myChart.setOption(option);
               
                // Make chart responsive
                window.addEventListener('resize', function() {{
                    myChart.resize();
                }});
            </script>
        </body>
        </html>
        """
       
        # Save the HTML to a file
        try:
            with open('visualization.html', 'w') as f:
                f.write(html)
            self.logger.info("Visualization HTML saved to visualization.html")
        except Exception as e:
            self.logger.error(f"Error saving visualization HTML: {e}")
       
        return html
 
    def generate_visualization(self, user_query, soql_result):
        """
        Generate ECharts visualization configuration based on user query and SOQL results.
       
        Args:
            user_query (str): The natural language query from the user
            soql_result (OrderedDict): The result from Salesforce query execution
           
        Returns:
            dict: ECharts configuration in JSON format
        """
        try:
            # Extract records and metadata from soql_result
            records = soql_result.get('records', [])
            total_size = soql_result.get('totalSize', 0)
           
            # Extract field names from the first record (excluding system fields)
            fields = []
            if records and len(records) > 0:
                fields = [k for k in records[0].keys() if not k.startswith('attributes')]
           
            # Define a color schema
            color_schema = ["#7da7e7 ", "#33FF57", "#3357FF", "#F1C40F", "#8E44AD"]  # Example color palette
           
            # Create prompt for visualization generation
            visualization_template = """
            You are an expert data visualization engineer. Based on the user's query and the data returned from a Salesforce SOQL query,
            generate an appropriate ECharts visualization configuration in JSON format.
           
            User Query: {user_query}
            Data Summary: {data_summary}
            Query Result Data: {soql_result}
           
            Analyze the data and query to determine the most appropriate chart type (bar, line, pie, scatter, etc.).
            Your response should be a valid JSON object containing the complete ECharts configuration.
           
            The configuration should include:
            1. Chart type
            2. Title based on the user query
            3. Appropriate axes labels (if applicable)
            4. Legend (if applicable)
            5. Data series properly formatted for the chart type
            6. Appropriate colors and styling, using the following color schema: {color_schema}
           
            Return ONLY the JSON configuration without any explanation or markdown formatting.
            """
           
            # Prepare data summary
            data_summary = f"Total records: {total_size}. Fields: {', '.join(fields) if fields else 'None'}"
           
            prompt = ChatPromptTemplate.from_template(visualization_template)
           
            chain = (
                    prompt
                    | self.llm
                    | StrOutputParser()
            )
           
            # Generate visualization configuration
            chart_config = chain.invoke({
                    "user_query": user_query,
                    "data_summary": data_summary,
                    "soql_result": str(soql_result),
                    "color_schema": color_schema  # Pass the color schema to the prompt
            })
           
            # Log the raw chart_config for debugging
            self.logger.info(f"Raw chart_config: {chart_config}")
           
            # Clean up the response to ensure it's valid JSON
            # Remove any markdown code block indicators
            chart_config = chart_config.replace("```json", "").replace("```", "").strip()
           
            # Validate and parse the string to ensure it's valid JSON
            import json
            try:
                chart_json = json.loads(chart_config)
            except json.JSONDecodeError as e:
                self.logger.error(f"JSON decoding error: {e} - Response: {chart_config}")
                return {
                    "title": {"text": "Error Generating Visualization"},
                    "series": [{"type": "bar", "data": []}]
                }
           
            self.logger.info("Successfully generated visualization configuration")
            return chart_json
           
        except Exception as e:
            self.logger.error(f"Error generating visualization: {str(e)}")
            self.logger.error(traceback.format_exc())
            # Return a basic error chart
            return {
                "title": {"text": "Error Generating Visualization"},
                "series": [{"type": "bar", "data": []}]
            }
       
 
 
# @mcp.tool()
# async def tool_soql(query: str)-> str:
#     """
#     SOQL query execution tool for Salesforce CRM data retrieval.
 
#     Examples:
#         - SELECT Name, Industry FROM Account WHERE Industry='Technology'
#         - SELECT COUNT() FROM Opportunity WHERE StageName='Closed Won'
 
#     Args:
#         query (str): The SOQL query to execute
#         tool_params (list): List of parameters for query execution
#     """
   
#     chat_history.append(HumanMessage(content=query))
#     salesforce_handler = SalesforceHandler()
#     sf=salesforce_handler.authenticate()
#     soql_query_response, soql_query, html_visualization = salesforce_handler.get_response(query, sf, chat_history)
   
#     # Save the visualization HTML to a file that can be accessed
#     if html_visualization:
#         try:
#             import os
#             visualization_path = os.path.join(os.getcwd(), 'visualization.html')
#             print(f"Visualization saved to: {visualization_path}")
#         except Exception as e:
#             print(f"Error with visualization path: {e}")
   
#     chat_history.append(AIMessage(content=soql_query_response))
#     return soql_query_response
from chatrequest import ChatRequest 
@mcp.tool()
async def tool_soql(query: str) -> str:
    """
        Chart Generation Tool for Salesforce Data Visualization.
    
        This tool processes a user query related to Salesforce CRM data, retrieves relevant data using SOQL,
        and generates an HTML-based visualization of the results. The function also returns a textual summary
        of the query's output. This tool also generates report including visualizations based on the query and the SOQL response.
    
        Examples:
            - "Show me the total revenue by industry."
            - "Generate a pie chart of opportunity stages."
            - "Visualize the distribution of leads by source."
            - "Generate a report of opportunities created in the last month."
    
        Args:
            query (str): A natural language query or SOQL-like request to fetch and visualize Salesforce data.
    """

    try:
        # Initialize chat_history if it doesn't exist in this scope
        if 'chat_history' not in globals():
            global chat_history
            chat_history = []
           
        chat_history.append(HumanMessage(content=query))
       
        # Add timeout for Salesforce authentication and operations
        salesforce_handler = SalesforceHandler()
        sf = await asyncio.wait_for(asyncio.to_thread(salesforce_handler.authenticate), timeout=10)
       
        # Execute the query with a timeout
        soql_response = await asyncio.wait_for(
            asyncio.to_thread(salesforce_handler.get_response, query, sf, chat_history),
            timeout=15
        )
       
        soql_query_response, soql_query, html_visualization = soql_response
       
        # Only handle visualization if present but don't let it block the response
        if html_visualization:
            try:
                import os
                visualization_path = os.path.join(os.getcwd(), 'visualization.html')
                with open(visualization_path, 'w') as f:
                    f.write(html_visualization)
                print(f"Visualization saved to: {visualization_path}")
            except Exception as e:
                print(f"Error with visualization path: {e}")
       
        chat_history.append(AIMessage(content=soql_query_response))
        return soql_query_response
       
    except asyncio.TimeoutError:
        return "The Salesforce operation timed out. Try simplifying your query or check your connection."
    except Exception as e:
        return f"Error executing SOQL query: {str(e)}"




@mcp.tool()
async def add_numbers(a: float, b: float,tool_params:ChatRequest) -> float:
    """
    Adds two numbers and returns the sum.

    Args:
        a (float): The first number
        b (float): The second number

    Returns:
        float: The sum of a and b
    """
    print("tool params in toollllll",tool_params)

    return a + b
 
# if __name__ == "__main__":
#     # query="Generate a pie chart of opportunity stages."
#     query="how many opportunities were creted by account manager Nazish Siddiqui?"
#     result=tool_soql(query)
#     print("Final Response###: ",result)
 
 
if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='sse')
 
 
#   def split_response(response):
#     """
#     Splits the LLM response into the SOQL response summary and the visualization config.
 
#     Args:
#         response (str): The complete LLM response string.
 
#     Returns:
#         tuple: A tuple containing the SOQL response summary and the visualization config.
#                Returns (None, None) if the response format is not as expected.
#     """
#     try:
#         # Split the response based on the delimiters
#         parts = response.split('(Visualization Config321@):')
#         soql_summary = parts[0].split('(SOQL response summary123@):')[1].strip()
#         visualization_config = parts[1].strip()
 
#         return soql_summary, visualization_config
#     except IndexError:
#         print("Unexpected response format.  Unable to split.")
#         return None, None
 
# # Example usage:
# response = "(SOQL response summary123@): There are 10 opportunities associated with the account manager Nazish \nSiddiqui.\n(Visualization Config321@): {'title': {'text': 'Opportunities Created by Nazish Siddiqui', 'left': 'center'}, 'tooltip': {'trigger': 'axis', 'axisPointer': {'type': 'shadow'}, 'formatter': '{b}: {c} Opportunities'}, 'grid': {'left': '3%', 'right': '4%', 'bottom': '3%', 'containLabel': True}, 'xAxis': [{'type': 'category', 'data': ['Nazish Siddiqui'], 'axisTick': {'alignWithLabel': True}, 'name': 'Account Manager', 'nameLocation': 'middle', 'nameGap': 30}], 'yAxis': [{'type': 'value', 'name': 'Number of Opportunities', 'nameLocation': 'middle', 'nameGap': 50, 'axisLabel': {'formatter': '{value}'}}], 'series': [{'name': 'Opportunities', 'type': 'bar', 'barWidth': '60%', 'data': [{'value': 10, 'itemStyle': {'color': '#7da7e7 '}}], 'label': {'show': True, 'position': 'top', 'formatter': '{c}'}}], 'color': ['#7da7e7 ', '#33FF57', '#3357FF', '#F1C40F', '#8E44AD']}"
 
# soql_summary, visualization_config = split_response(response)
 
# if soql_summary and visualization_config:
#     print("SOQL Summary:", soql_summary)
#     print("Visualization Config:", visualization_config)  
