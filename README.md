# horta-back — API de Irrigação IoT

Backend FastAPI para sistema de irrigação automatizada com ESP32. Controla sensores de umidade, zonas de irrigação, agendamentos e uma bomba d'água via API REST.

---

## Stack

- **Python 3.13**
- **FastAPI 0.116** + **Uvicorn 0.35** (servidor ASGI)
- **SQLAlchemy 2.0** async + **aiosqlite** (banco local) / **asyncpg** (PostgreSQL)
- **Pydantic v2** + **pydantic-settings**
- **Passlib + bcrypt** (hash de senhas)
- **python-dotenv** (variáveis de ambiente)
- Scheduler próprio em `asyncio` (sem dependências externas)

---

## Estrutura de pastas

```
horta-back/
├── main.py                     # entry point — FastAPI app + lifespan + scheduler
├── Procfile                    # comando de start para Railway
├── requirements.txt
├── .env.example                # variáveis de ambiente necessárias
│
├── core/
│   ├── configs.py              # Settings (DB_URL, FERNET_KEY lidos do ambiente)
│   ├── database.py             # engine async + SessionLocal
│   ├── deps.py                 # get_session (dependency injection)
│   └── scheduler.py            # loop asyncio que dispara agendamentos a cada 60s
│
├── models/
│   ├── __all_models.py         # importa todos os models (garante registro no metadata)
│   ├── agendamento_model.py    # Agendamento
│   ├── execucao_model.py       # ExecucaoIrrigacao
│   └── zonas_model.py          # ZonaSensor (+ Controlador e Sensor no mesmo arquivo)
│
├── schemas/
│   ├── agendamento_schema.py
│   ├── controlador_schema.py
│   ├── execucao_schema.py
│   ├── leitura_sensor_schema.py
│   ├── sensor_schema.py
│   ├── user_schema.py
│   └── zonas_schema.py
│
└── api/v1/
    ├── api.py                  # monta todos os routers
    └── endpoints/
        ├── users.py
        ├── controlador.py
        ├── sensor.py
        ├── zona_sensor.py
        ├── leitura_sensor.py
        ├── agendamento.py
        ├── bomba.py
        └── execucoes.py
```

---

## Modelos do banco de dados

```
User            — usuários com autenticação (bcrypt)
Controlador     — dispositivos ESP32 cadastrados
Sensor          — sensores físicos (tipo, unidade de medida)
ZonaSensor      — zona de irrigação (vincula Controlador + Sensor)
LeituraSensor   — leitura de umidade enviada pelo ESP32
Agendamento     — horário/regra de irrigação automática
ExecucaoIrrigacao — log de cada irrigação executada (manual ou agendada)
```

### Relacionamentos
```
Controlador  1──N  ZonaSensor
Sensor       1──N  ZonaSensor
ZonaSensor   1──N  Agendamento
ZonaSensor   1──N  ExecucaoIrrigacao
Agendamento  1──N  ExecucaoIrrigacao
```

---

## Endpoints

Prefixo base: `/api/v1`

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/users/` | Criar usuário |
| GET | `/users/` | Listar usuários |
| POST | `/controladores/` | Cadastrar controlador |
| GET | `/controladores/` | Listar controladores |
| POST | `/sensores/` | Cadastrar sensor |
| GET | `/sensores/` | Listar sensores |
| POST | `/zonas/` | Criar zona |
| GET | `/zonas/` | Listar zonas |
| POST | `/leitura/` | Registrar leitura do sensor (chamado pelo ESP32) |
| GET | `/leitura/sensor/{id}/latest` | Última leitura de um sensor |
| GET | `/leitura/sensor/{id}` | Histórico de leituras (filtro por data ou `?dias=N`) |
| GET | `/leitura/` | Últimas leituras (`?limit=100`, máx 1000) |
| POST | `/agendamento/` | Criar agendamento |
| GET | `/agendamento/` | Listar agendamentos |
| GET | `/agendamento/{id}` | Buscar agendamento |
| PUT | `/agendamento/{id}` | Atualizar agendamento |
| DELETE | `/agendamento/{id}` | Deletar agendamento |
| POST | `/agendamento/{id}/executar` | Disparar irrigação manualmente via agendamento |
| POST | `/bomba/ligar` | Ligar bomba (manual, com duração em minutos) |
| POST | `/bomba/desligar` | Desligar bomba manualmente |
| GET | `/bomba/status` | Estado atual da bomba `{"ligada": bool, "id_execucao_ativa": int\|null}` |
| GET | `/execucoes/` | Histórico de execuções (filtros: zona, tipo, data) |
| POST | `/execucoes/` | Criar execução manualmente |
| GET | `/ping` | Health check — retorna `{"msg": "pong!"}` |

Documentação interativa disponível em `/docs` (Swagger UI).

---

## Scheduler

O arquivo `core/scheduler.py` roda um loop `asyncio` que acorda a cada **60 segundos** e verifica todos os agendamentos ativos. Para cada um:

1. Compara `hora_inicio` (zerado em segundos) com a hora atual em **Brasília (UTC-3)**
2. Checa se já foi executado hoje
3. Checa a regra de repetição: `repetir_todos_dias`, `dias_semana` (`"seg,qua,sex"`) ou `intervalo_dias`
4. Se tudo bate: cria um registro `ExecucaoIrrigacao`, liga a bomba e agenda o desligamento automático após `duracao_minutos`

---

## Lógica da bomba

Estado em memória (`_estado` em `bomba.py`):
```python
{"ligada": False, "id_execucao_ativa": None}
```

- `POST /bomba/ligar` retorna `409` se a bomba já estiver em uso
- `_auto_completar` desliga a bomba após a duração configurada; usa `try/finally` para garantir reset do estado mesmo em caso de erro de banco
- `GET /bomba/status` é o endpoint consultado pelo ESP32 a cada 30 segundos

---

## Variáveis de ambiente

| Variável | Obrigatória | Padrão | Descrição |
|----------|-------------|--------|-----------|
| `DATABASE_URL` | Não | SQLite local | URL do banco. Ex: `postgresql://user:pass@host/db` |
| `FERNET_KEY` | Não | chave dev embutida | Chave de criptografia Fernet |

> **Atenção:** em produção, sempre defina `FERNET_KEY` com uma chave nova gerada por:
> ```bash
> python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
> ```

O `DATABASE_URL` com prefixo `postgresql://` é automaticamente convertido para `postgresql+asyncpg://` pelo `configs.py`.

---

## Rodar localmente

```bash
# 1. Clonar e entrar na pasta
git clone https://github.com/ViniciusLira1/horta-back.git
cd horta-back

# 2. Ambiente virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Dependências
pip install -r requirements.txt

# 4. Iniciar
python main.py
# ou
uvicorn main:app --reload
```

Acesse `http://localhost:8000/docs` para ver a documentação da API.

---

## Deploy no PythonAnywhere (SQLite — recomendado para projeto pequeno)

PythonAnywhere tem disco persistente, então o SQLite é mantido entre deploys.

### 1. Abrir um console Bash no PythonAnywhere
```bash
git clone https://github.com/ViniciusLira1/horta-back.git
cd horta-back
python3.13 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configurar o Web App
- **Web → Add a new web app → Manual configuration → Python 3.13**
- Em **Source code**: `/home/SEUUSUARIO/horta-back`
- Em **Virtualenv**: `/home/SEUUSUARIO/horta-back/venv`

### 3. Editar o arquivo WSGI
Abrir o arquivo WSGI gerado (`/var/www/SEUUSUARIO_pythonanywhere_com_wsgi.py`) e substituir tudo por:

```python
import sys
sys.path.insert(0, '/home/SEUUSUARIO/horta-back')

from main import app as application
```

### 4. Variáveis de ambiente (aba Web → Environment variables)
```
FERNET_KEY=sua_chave_gerada_aqui
```
`DATABASE_URL` não é necessário — o app usa SQLite por padrão.

### 5. Reload
Clicar em **Reload** na aba Web. A URL pública será:
```
https://SEUUSUARIO.pythonanywhere.com
```

---

## Deploy no Railway (PostgreSQL)

```bash
# Conectar repo GitHub no Railway
# Adicionar plugin PostgreSQL
# Definir variáveis de ambiente:
#   DATABASE_URL  →  referência ao PostgreSQL do Railway (${{Postgres.DATABASE_URL}})
#   FERNET_KEY    →  chave gerada localmente
```

O `Procfile` já está configurado:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

## Firmware ESP32

O ESP32 se comunica com dois endpoints:

| Endpoint | Método | Intervalo | Payload |
|----------|--------|-----------|---------|
| `/api/v1/leitura/` | POST | 30 min | `{"id_sensor": 1, "valor": 72.5}` |
| `/api/v1/bomba/status` | GET | 30 s | — |

Resposta do `/bomba/status`:
```json
{"ligada": true, "id_execucao_ativa": 42}
```

O ESP32 lê `ligada` e aciona o pino digital que comanda o relay da bomba.
