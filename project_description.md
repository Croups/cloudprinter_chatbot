Create a Conversational AI Chatbot / AI Agent  
Objective: To develop a conversational AI chatbot that provides price information for print products by communicating with Cloudprinter.com's Quote API and Product API. The chatbot will engage in a natural conversation with users to gather necessary details and provide accurate pricing information. The file check functionality will be excluded for this phase.

Project Purpose: This project is primarily intended to get acquainted with talented AI developers who can take on large projects in the short term.
Project Scope:
1.	Requirements Gathering:
o	Understand the detailed requirements and use cases for the chatbot.
o	Review the API documentation provided by Cloudprinter.com for the Quote API and Product API as listed at https://docs.cloudprinter.com/connected-apps/
o	Identify the key functionalities and interactions needed for the chatbot. See as example the chat conversation below in the document.
2.	Design Phase:
o	Design the conversational flow for the chatbot, including user prompts and responses.
o	Define the data mapping between product names and product codes using the Product API.
o	Create a detailed architecture diagram for the chatbot, including API integration points.
3.	Development Phase:
o	Set up the development environment and necessary tools.
o	Implement the chatbot's core functionality, including:
	Natural Language Processing (NLP) to understand user queries in any language using existing AI models of Claude/ChatGTP or others. 
	Integration with the Product API to fetch product specifications and map product names to product codes.
	Integration with the Quote API to retrieve pricing information based on user inputs.
o	Develop the conversational logic to handle user interactions and gather necessary details (e.g., paper type, weight, laminate options, delivery location).
o	Implement error handling and validation to ensure robust performance.
4.	Testing Phase:
o	Conduct unit testing for individual components and API integrations.
o	Perform end-to-end testing of the chatbot to ensure it provides accurate and relevant responses.
o	Test the chatbot with various user scenarios to validate its conversational flow and error handling.
5.	Deployment Phase:
o	Deploy the chatbot on a simple blank page for initial testing and feedback.
o	Monitor the chatbot's performance and gather user feedback for further improvements.
o	Prepare documentation for the chatbot's setup, usage, and maintenance.
Timeline: 1 week between acceptance of job and final delivery
Budget: The budget for this project is $500 - $700, depending on the developer's experience and the quality of work delivered.
________________________________________
Example of chat conversation: 

This chat is based on loading product specifications and info and combinations based on the input from user. 

https://api.cloudprinter.com/cloudcore/1.0/products This return all products
https://api.cloudprinter.com/cloudcore/1.0/products/info This for options
If client doesn’t know size; Bot will call products api  >> get all book sizes. When choosing the size, the Qoute Api will be pinged for a price and delivery options.:

Visitor: Hi, I would like to know the price for 100 business cards in the Netherlands.
cloudprinter.com: Hello! I'd be happy to help you with that. Could you please specify the type of paper you would like for the business cards?
Visitor: I would like them to be printed on glossy paper.
cloudprinter.com: Great choice! What weight of paper would you prefer for the business cards? We have options like 250gsm, 300gsm, and 350gsm.
Visitor: I think 300gsm would be good.
cloudprinter.com: Excellent! Would you like to add a laminate coating to the business cards? We offer options like matte, glossy, or no laminate.
Visitor: Let's go with a glossy laminate.
cloudprinter.com: Perfect! Which city in the Netherlands would you like the business cards to be delivered to?
Visitor: Amsterdam.
cloudprinter.com: Thank you! Just to confirm, you would like 100 business cards printed on 300gsm glossy paper with a glossy laminate, delivered to Amsterdam, correct?
Visitor: Yes, that's correct.
cloudprinter.com: Great! We have two delivery options: you can choose to have them delivered tomorrow for an additional €5, or the day after tomorrow at no extra cost. Which option would you prefer?
Visitor: Tomorrow, please.
cloudprinter.com: Wonderful! The price for 100 business cards printed on 300gsm glossy paper with a glossy laminate, delivered to Amsterdam tomorrow is €35. This price is based on our standard starter pricing. If you have a subscription, the product price can be even lower.
