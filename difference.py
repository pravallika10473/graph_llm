import openai
from dotenv import load_dotenv
import os

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def get_difference(netlist1, netlist2, performance1, performance2):
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"This is netlist1:{netlist1} and This is its performance:{performance1}\nThis is netlist2:{netlist2}\n\nThis is its performance:{performance2}, what connection difference by comparing netlists thats causing these performance difference?" }]
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    netlist1 = open("netlist/paper1/fig3.txt", "r").read()
    netlist2 = open("netlist/paper2/fig3.txt", "r").read()
    performance1 = {"Vref": 1.09, "Power dissipation": 0.100, "Temperature range": [-40, 120]}
    performance2 = {"Vref": 1.18, "Power dissipation": 0.108, "Temperature range": [-20, -80]}
    print(get_difference(netlist1, netlist2, performance1, performance2))
    