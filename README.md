# app overview: stack and pipeline
--- 
## tech stack: FARM + Airflow ETL
- database: [MongoDB](https://www.mongodb.com/)
- DB cache: [Redis](https://redis.io/)
- backend: [FastAPI](https://fastapi.tiangolo.com/)
	- Python 3.9 
	- [Beanie](https://roman-right.github.io/beanie/) for async DB interaction 
- frontend: [Next.js](https://nextjs.org/)
- ETL orchestration: [Apache Airflow](https://airflow.apache.org/)
- IDE: vsCodium

## CI/CD pipeline:
- Static analysis: 
	- Pylint for python
	- ESLint for react
- Build
	- dockerize application 
- deploy
	- AWS, GCP, Azure, etc.
- dynamic analysis
	- OWASP ZAP to identify security vulnerabilities