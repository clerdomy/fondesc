#!/bin/bash

# Configurações
BACKUP_DIR="/var/backups/django"
PROJECT_DIR="/caminho/para/seu/projeto"
DB_NAME="seu_banco_de_dados"
DB_USER="seu_usuario_db"
DB_PASS="sua_senha_db"
DATE=$(date +%Y-%m-%d_%H-%M-%S)
RETENTION_DAYS=7

# Criar diretório de backup se não existir
mkdir -p $BACKUP_DIR

# Backup do banco de dados PostgreSQL
pg_dump -U $DB_USER -h localhost $DB_NAME | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Backup dos arquivos do projeto
tar -czf $BACKUP_DIR/files_backup_$DATE.tar.gz -C $(dirname $PROJECT_DIR) $(basename $PROJECT_DIR) --exclude="*.pyc" --exclude="__pycache__" --exclude="venv" --exclude="node_modules"

# Backup dos arquivos de mídia
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz -C $PROJECT_DIR/media .

# Remover backups antigos
find $BACKUP_DIR -name "db_backup_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "files_backup_*.tar.gz" -type f -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "media_backup_*.tar.gz" -type f -mtime +$RETENTION_DAYS -delete

# Registrar backup
echo "Backup concluído em $(date)" >> $BACKUP_DIR/backup_log.txt

# Opcional: Enviar backup para armazenamento remoto (exemplo com rclone para Google Drive)
# rclone copy $BACKUP_DIR/db_backup_$DATE.sql.gz gdrive:django-backups/
# rclone copy $BACKUP_DIR/files_backup_$DATE.tar.gz gdrive:django-backups/
# rclone copy $BACKUP_DIR/media_backup_$DATE.tar.gz gdrive:django-backups/