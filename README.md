# FONDESC - Fòmasyon Nasyonal a Distans

**Status:** Em desenvolvimento 🚧

## Sobre o Projeto

FONDESC (Fòmasyon Nasyonal a Distans) é uma plataforma web baseada em Django voltada para a educação e gestão de cursos, com o objetivo de fornecer formação a distância para o Haiti. Este projeto nasceu da necessidade de oferecer uma alternativa acessível e eficiente para a educação online no país, permitindo que mais pessoas tenham acesso ao conhecimento, independentemente de sua localização ou condições financeiras.

## Funcionalidades

- 📚 **Gerenciamento de Cursos**: Cadastro, edição e exclusão de cursos.
- 👩‍🏫 **Gestão de Professores**: Informações sobre docentes e suas disciplinas.
- 👨‍🎓 **Autenticação de Usuários**: Sistema de login e registro seguro.
- 📱 **Design Responsivo**: Interface adaptável para dispositivos móveis e desktops.

## Tecnologias Utilizadas

- **Backend:** Django
- **Frontend:** HTML, CSS, JavaScript
- **Banco de Dados:** SQLite (padrão, podendo ser substituído por PostgreSQL ou MySQL no futuro)

## Estrutura do Projeto

O projeto segue a estrutura padrão do Django com algumas aplicações customizadas:

```
fondesc/
│── fondesc/          # Configurações principais do projeto
│── fondescapp/       # Aplicativo principal
│   ├── migrations/   # Migrações do banco de dados
│   ├── static/       # Arquivos estáticos (CSS, JS, imagens)
│   ├── templates/    # Templates HTML
│── manage.py         # Ferramenta de linha de comando do Django
```

## Como Instalar e Rodar o Projeto

### 1. Clonar o repositório

```sh
git clone git@github.com:clerdomy/fondesc.git
cd fondesc
```

### 2. Criar e ativar um ambiente virtual

```sh
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

### 3. Instalar as dependências

```sh
pip install -r requirements.txt
```

### 4. Aplicar as migrações do banco de dados

```sh
python manage.py migrate
```

### 5. Criar um superusuário (admin)

```sh
python manage.py createsuperuser
```

### 6. Rodar o servidor de desenvolvimento

```sh
python manage.py runserver
```

### 7. Acessar a aplicação

Abra o navegador e acesse:

```
http://localhost:8000/
```

## Como Contribuir

Se você deseja contribuir para o desenvolvimento do FONDESC, siga os seguintes passos:

1. **Fork** este repositório.
2. Crie uma **branch** para sua funcionalidade/ajuste.
3. Faça um **commit** claro e objetivo.
4. Envie um **Pull Request**.

Consulte o arquivo `CONTRIBUTING.md` para mais detalhes sobre como contribuir.

## Licença

Este projeto é licenciado sob a [MIT License](https://opensource.org/licenses/MIT).

---

FONDESC - Facilitando o acesso à educação a distância no Haiti 🇭🇹

