# water-tracker


## Запуск проекта

```bash
cd water-tracker
docker build -t water-tracker -f backend/Dockerfile . && docker run -p 8000:8000 water-tracker
```