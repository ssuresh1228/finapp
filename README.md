# app overview: stack and pipeline
--- 
## tech stack: FARM + Airflow ETL
- database: [MongoDB](https://www.mongodb.com/)
- DB cache: [Redis](https://redis.io/)
- backend: [FastAPI](https://fastapi.tiangolo.com/)
	- python 3.12.0 
	- [Beanie](https://roman-right.github.io/beanie/) for async DB interaction 
- frontend: [React.js](https://react.dev/)
- ETL orchestration: [Apache Airflow](https://airflow.apache.org/)
- IDE: vsCodium

## CI/CD pipeline:
- Static analysis: 
	- Pylint for python
	- ESLint for react
- Build
	- dockerize application 
- deploy
	- AWS
- dynamic analysis
	- OWASP ZAP to identify security vulnerabilities
