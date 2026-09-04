from mcp.server.fastmcp import FastMCP
from notion_client import Client
import os
import sys

# Inicializa o servidor FastMCP
mcp = FastMCP("Notion MCP")

# Configuração do Notion Client
# O token deve ser passado como variável de ambiente NOTION_TOKEN
notion_token = os.environ.get("NOTION_TOKEN")
if not notion_token:
    print("Aviso: Variável de ambiente NOTION_TOKEN não está configurada.", file=sys.stderr)
    notion = None
else:
    notion = Client(auth=notion_token)

@mcp.tool()
def search_notion(query: str) -> str:
    """
    Busca por páginas ou bancos de dados no Notion.
    """
    if not notion:
        return "Erro: NOTION_TOKEN não configurado no servidor."
        
    try:
        results = notion.search(query=query).get("results", [])
        if not results:
            return f"Nenhum resultado encontrado para '{query}'."
            
        output = []
        for item in results[:10]: # Limita aos 10 primeiros
            title = "Sem Título"
            
            # Extrair título dependendo do tipo de objeto
            if item["object"] == "page":
                if "title" in item.get("properties", {}):
                    props = item["properties"]
                    for k, v in props.items():
                        if v["type"] == "title" and v["title"]:
                            title = v["title"][0]["plain_text"]
                            break
                elif "Name" in item.get("properties", {}) and item["properties"]["Name"]["type"] == "title":
                     if item["properties"]["Name"]["title"]:
                         title = item["properties"]["Name"]["title"][0]["plain_text"]

            elif item["object"] == "database":
                if item.get("title"):
                    title = item.get("title")[0]["plain_text"]
                    
            output.append(f"- {title} (ID: {item['id']}, Tipo: {item['object']})")
            
        return "\n".join(output)
    except Exception as e:
        return f"Falha ao buscar no Notion: {str(e)}"

@mcp.tool()
def create_page_in_db(database_id: str, title: str) -> str:
    """
    Cria uma nova página em um banco de dados específico do Notion.
    """
    if not notion:
         return "Erro: NOTION_TOKEN não configurado no servidor."
         
    try:
        new_page = notion.pages.create(
            parent={"database_id": database_id},
            properties={
                "Name": { # 'Name' é o nome padrão da propriedade de título na maioria dos DBs
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                }
            }
        )
        return f"Página '{title}' criada com sucesso! ID: {new_page['id']}"
    except Exception as e:
        return f"Falha ao criar página: {str(e)}"

if __name__ == "__main__":
    # Inicia o servidor via stdin/stdout
    mcp.run()

