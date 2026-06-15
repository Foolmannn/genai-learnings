# We want : if report is long then call llm to summarize and if short report then print as it is 
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

from langchain_core.runnables import RunnableParallel,RunnableBranch,RunnableSequence,RunnablePassthrough

load_dotenv()

prompt1 = PromptTemplate(
    template="Generate a detailed report on :  {topic}",
    input_variables=['topic']
)

prompt2 = PromptTemplate(
    template= "Generate a summary on the Following report: {text}",
    input_variables=['text']
)

model=ChatGoogleGenerativeAI(model='gemini-3.1-flash-lite')

parser = StrOutputParser()

# creating the first sequence for report generation

report_gen_chain = prompt1 | model | parser

branch_chain = RunnableBranch(  # we send the conditions on the tuple format . ( (condition1, runnable to execute) ,(anothercondition , runnable to execute for this condition ) , default runnable  )
    # (lambda x: len(x.split())>500  ,     RunnableSequence(prompt2,model,parser)),
    (lambda x: len(x.split())>200  ,     RunnableSequence(prompt2,model,parser)),
    RunnablePassthrough()
    
)

final_chain = report_gen_chain | branch_chain

result = final_chain.invoke({'topic': "GenZ revolution in Nepal"})

print(result)

# so we can see when word count is more tha n 300 the branch triggers and summary is created. 

"""

### **Executive Summary: The Gen Z Revolution in Nepal**


This report analyzes the transformative role of Nepal’s Gen Z (born 1997–2012) as they reshape the nation’s socio-political and economic landscape. Moving away from traditional hierarchies, this cohort is leveraging digital connectivity to challenge the status quo and demand a more meritocratic future.

#### **Key Drivers**
*   **Digital Empowerment:** Unprecedented internet access has allowed youth to consume global discourse and bypass traditional media gatekeepers.
*   **Economic Despair:** The daily migration of thousands of youth (the "brain drain") has fueled deep resentment toward domestic governance.
*   **Political Disillusionment:** A collective rejection of traditional political parties following failures in stability and public service delivery.

#### **Major Areas of Impact**
*   **Political Disruption:** Gen Z served as the "digital vanguard" in the 2022 elections, favoring independent candidates and implementing a culture of public accountability through social media documentation.
*   **Economic Evolution:** A shift away from traditional government employment toward the creator economy, digital entrepreneurship, and fintech innovation.
*   **Cultural Modernization:** A proactive stance on breaking patriarchal and caste-based taboos, while championing LGBTQ+ rights, mental health, and climate action.

#### **Critical Challenges**
*   **Sustainability:** Digital activism risks becoming "slacktivism" or falling into echo chambers.
*   **Institutional Entrenchment:** Powerful patronage-based political systems are difficult to dismantle via electoral wins alone.
*   **The Migration Paradox:** The constant exodus of the most capable youth risks hollowing out the leadership pool necessary for sustained institutional reform.

#### **Future Outlook**
The movement is entering a critical **"protest-to-policy"** transition. The next five years will determine if independent political experiments can successfully institutionalize their platforms. Additionally, the role of the Nepali diaspora, who are now using their influence and resources to support reformist candidates, will be a defining factor in Nepal’s political trajectory.

**Conclusion:** Nepal’s Gen Z is driving a tectonic shift in public consciousness. While systemic barriers remain, they have successfully moved the political Overton window, forcing a race between necessary national reform and the persistent demographic drain of the youth population.


"""


"""
The Gen Z "revolution" is a profound cultural and systemic shift rather than a singular movement. The report concludes that while their political and technological influence will inevitably reshape Nepal, the country’s future hinges on its ability to modernize its institutions enough to retain the talent and ambition of this cohort.
"""