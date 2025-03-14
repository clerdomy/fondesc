import random
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from courses.models import Category, Course, Module, Lesson, Quiz, Question, Answer
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
import os
from django.conf import settings

User = get_user_model()

class Command(BaseCommand):
    help = 'Cria 10 cursos de teste para a plataforma'

    def handle(self, *args, **kwargs):
        # Verificar se já existem cursos
        if Course.objects.exists():
            self.stdout.write(self.style.WARNING('Já existem cursos no banco de dados. Deseja continuar? (s/n)'))
            answer = input()
            if answer.lower() != 's':
                self.stdout.write(self.style.SUCCESS('Operação cancelada.'))
                return

        # Criar categorias se não existirem
        categories = [
            'Desenvolvimento Web',
            'Ciência de Dados',
            'Automação',
            'Machine Learning',
            'Desenvolvimento de Jogos'
        ]
        
        category_objects = {}
        for category_name in categories:
            category, created = Category.objects.get_or_create(
                name=category_name,
                slug=slugify(category_name)
            )
            category_objects[category_name] = category
            if created:
                self.stdout.write(self.style.SUCCESS(f'Categoria "{category_name}" criada com sucesso!'))
            else:
                self.stdout.write(self.style.WARNING(f'Categoria "{category_name}" já existe.'))

        # Verificar se existe um usuário instrutor
        try:
            instructor = User.objects.get(username='instructor')
            self.stdout.write(self.style.SUCCESS('Instrutor encontrado.'))
        except User.DoesNotExist:
            # Criar um usuário instrutor
            instructor = User.objects.create_user(
                username='instructor',
                email='instructor@example.com',
                password='instructor123',
                first_name='João',
                last_name='Silva',
                user_type='instructor',
                expertise='Python, Django, Data Science'
            )
            self.stdout.write(self.style.SUCCESS('Instrutor criado com sucesso!'))

        # Dados dos cursos
        courses_data = [
            {
                'title': 'Python para Iniciantes',
                'description': 'Aprenda os fundamentos da programação Python, incluindo sintaxe básica, estruturas de dados, funções e orientação a objetos. Este curso é perfeito para quem está começando a programar ou quer migrar de outra linguagem para Python.',
                'short_description': 'Domine os conceitos básicos de Python e comece sua jornada de programação.',
                'category': category_objects['Desenvolvimento Web'],
                'price': 49.99,
                'level': 'beginner',
                'duration_in_weeks': 4,
            },
            {
                'title': 'Django: Desenvolvimento Web com Python',
                'description': 'Aprenda a construir aplicações web robustas e escaláveis com Django, o framework web mais popular do Python. Você aprenderá sobre modelos, views, templates, formulários, autenticação e muito mais.',
                'short_description': 'Construa aplicações web completas com o framework Django.',
                'category': category_objects['Desenvolvimento Web'],
                'price': 69.99,
                'level': 'intermediate',
                'duration_in_weeks': 6,
            },
            {
                'title': 'Análise de Dados com Pandas',
                'description': 'Domine a biblioteca Pandas para análise e manipulação de dados em Python. Aprenda a importar, limpar, transformar e visualizar dados para extrair insights valiosos.',
                'short_description': 'Transforme e analise dados com a poderosa biblioteca Pandas.',
                'category': category_objects['Ciência de Dados'],
                'price': 59.99,
                'level': 'intermediate',
                'duration_in_weeks': 5,
            },
            {
                'title': 'Machine Learning com Python',
                'description': 'Introdução aos conceitos fundamentais de machine learning usando Python e scikit-learn. Aprenda sobre regressão, classificação, clustering e como avaliar modelos de machine learning.',
                'short_description': 'Aprenda a criar modelos de machine learning para resolver problemas reais.',
                'category': category_objects['Machine Learning'],
                'price': 79.99,
                'level': 'advanced',
                'duration_in_weeks': 8,
            },
            {
                'title': 'Automação com Python',
                'description': 'Aprenda a automatizar tarefas repetitivas com Python. Este curso aborda automação de planilhas, web scraping, manipulação de arquivos, envio de e-mails e muito mais.',
                'short_description': 'Economize tempo automatizando tarefas do dia a dia com Python.',
                'category': category_objects['Automação'],
                'price': 54.99,
                'level': 'beginner',
                'duration_in_weeks': 4,
            },
            {
                'title': 'Python para Ciência de Dados',
                'description': 'Um curso abrangente sobre o ecossistema Python para ciência de dados, incluindo NumPy, Pandas, Matplotlib e Seaborn. Aprenda a analisar e visualizar dados de forma eficiente.',
                'short_description': 'Domine as principais bibliotecas Python para análise e visualização de dados.',
                'category': category_objects['Ciência de Dados'],
                'price': 69.99,
                'level': 'intermediate',
                'duration_in_weeks': 6,
            },
            {
                'title': 'Desenvolvimento de APIs com Flask',
                'description': 'Aprenda a criar APIs RESTful com Flask, um microframework web para Python. Este curso aborda rotas, autenticação, documentação e deploy de APIs.',
                'short_description': 'Construa APIs web rápidas e eficientes com Flask.',
                'category': category_objects['Desenvolvimento Web'],
                'price': 59.99,
                'level': 'intermediate',
                'duration_in_weeks': 5,
            },
            {
                'title': 'Deep Learning com PyTorch',
                'description': 'Mergulhe no mundo do deep learning com PyTorch. Aprenda a criar e treinar redes neurais para resolver problemas complexos de classificação, regressão e geração de conteúdo.',
                'short_description': 'Domine técnicas avançadas de deep learning com PyTorch.',
                'category': category_objects['Machine Learning'],
                'price': 89.99,
                'level': 'advanced',
                'duration_in_weeks': 10,
            },
            {
                'title': 'Desenvolvimento de Jogos com Pygame',
                'description': 'Aprenda a criar jogos 2D com Pygame, uma biblioteca Python para desenvolvimento de jogos. Este curso aborda gráficos, animações, colisões, sons e muito mais.',
                'short_description': 'Crie seus próprios jogos 2D com Python e Pygame.',
                'category': category_objects['Desenvolvimento de Jogos'],
                'price': 64.99,
                'level': 'intermediate',
                'duration_in_weeks': 7,
            },
            {
                'title': 'Python Avançado: Recursos Poderosos',
                'description': 'Explore recursos avançados do Python como geradores, decoradores, metaclasses, concorrência e muito mais. Este curso é ideal para programadores que já dominam o básico de Python.',
                'short_description': 'Leve suas habilidades em Python para o próximo nível.',
                'category': category_objects['Desenvolvimento Web'],
                'price': 74.99,
                'level': 'advanced',
                'duration_in_weeks': 8,
            },
        ]

        # Criar uma imagem de placeholder para os cursos
        def create_placeholder_image(width, height, name):
            # Verificar se o diretório media existe
            media_dir = os.path.join(settings.MEDIA_ROOT, 'course_thumbnails')
            os.makedirs(media_dir, exist_ok=True)
            
            # Criar um arquivo de imagem simples
            content = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg"><rect width="100%" height="100%" fill="#3776ab"/><text x="50%" y="50%" font-family="Arial" font-size="24" fill="white" text-anchor="middle" dominant-baseline="middle">{name}</text></svg>'
            return SimpleUploadedFile(name=f"{slugify(name)}.svg", content=content.encode('utf-8'), content_type='image/svg+xml')

        # Criar os cursos
        created_courses = []
        for course_data in courses_data:
            # Criar thumbnail
            thumbnail = create_placeholder_image(800, 450, course_data['title'])
            
            # Criar o curso
            course = Course.objects.create(
                title=course_data['title'],
                slug=slugify(course_data['title']),
                description=course_data['description'],
                short_description=course_data['short_description'],
                category=course_data['category'],
                instructor=instructor,
                thumbnail=thumbnail,
                price=course_data['price'],
                level=course_data['level'],
                duration_in_weeks=course_data['duration_in_weeks'],
                is_published=True
            )
            created_courses.append(course)
            self.stdout.write(self.style.SUCCESS(f'Curso "{course.title}" criado com sucesso!'))
            
            # Criar módulos para o curso
            num_modules = random.randint(3, 5)
            for i in range(1, num_modules + 1):
                module = Module.objects.create(
                    course=course,
                    title=f'Módulo {i}: {random.choice(["Introdução", "Conceitos Básicos", "Fundamentos", "Técnicas Avançadas", "Aplicações Práticas"])}',
                    description=f'Este módulo aborda os principais conceitos de {course.title} com exemplos práticos e exercícios.',
                    order=i
                )
                
                # Criar lições para o módulo
                num_lessons = random.randint(3, 6)
                for j in range(1, num_lessons + 1):
                    lesson = Lesson.objects.create(
                        module=module,
                        title=f'Lição {j}: {random.choice(["Introdução", "Conceitos", "Prática", "Exemplos", "Exercícios", "Revisão"])}',
                        content=f'<h2>Conteúdo da Lição {j}</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam euismod, nisl eget aliquam ultricies, nunc nisl aliquet nunc, quis aliquam nisl nunc eu nisl.</p><h3>Subtítulo</h3><p>Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Vestibulum tortor quam, feugiat vitae, ultricies eget, tempor sit amet, ante.</p><pre><code>print("Hello, World!")</code></pre>',
                        video_url='https://www.youtube.com/embed/dQw4w9WgXcQ',  # Placeholder
                        order=j,
                        duration_in_minutes=random.randint(10, 30)
                    )
                    
                    # Criar quiz para algumas lições
                    if random.choice([True, False]):
                        quiz = Quiz.objects.create(
                            lesson=lesson,
                            title=f'Quiz: {lesson.title}',
                            description='Teste seus conhecimentos sobre esta lição.',
                            pass_percentage=70
                        )
                        
                        # Criar perguntas para o quiz
                        num_questions = random.randint(3, 5)
                        for k in range(1, num_questions + 1):
                            question = Question.objects.create(
                                quiz=quiz,
                                text=f'Pergunta {k}: Qual é a saída do seguinte código Python?\n```python\nprint("Hello" + " " + "World")\n```',
                                order=k
                            )
                            
                            # Criar respostas para a pergunta
                            Answer.objects.create(
                                question=question,
                                text='Hello World',
                                is_correct=True
                            )
                            Answer.objects.create(
                                question=question,
                                text='HelloWorld',
                                is_correct=False
                            )
                            Answer.objects.create(
                                question=question,
                                text='Hello + World',
                                is_correct=False
                            )
                            Answer.objects.create(
                                question=question,
                                text='Error',
                                is_correct=False
                            )

        self.stdout.write(self.style.SUCCESS(f'Total de {len(created_courses)} cursos criados com sucesso!'))

