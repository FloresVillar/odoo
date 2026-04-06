NAME?=mi_modulo
CONTAINER_WEB?=odoo-web-1
CONTAINER_DB?=odoo-db-1

.PHONY: up permisos scaffold rebuild logs restart upgrade

up: 
	docker compose up -d  

permisos: up
	$(eval CONTAINER_NAME=$(shell docker compose ps web --format "{{.Name}}"))
	@echo "Detectando contenedor"
	docker exec -u 0 $(CONTAINER_NAME) chmod -R 777 /mnt/extra-addons
	sudo chown -R $(shell whoami):$(shell whoami) ./addons
	
scaffold: permisos
	$(eval CONTAINER_NAME=$(shell docker compose ps web --format "{{.Name}}"))
	docker exec -u 0 $(CONTAINER_NAME) odoo scaffold $(NAME) /mnt/extra-addons
	@echo "Modulo $(NAME) creado y con permisos dde usuario no root"
	sudo chown -R $(shell whoami):$(shell whoami) ./addons

logs:
	@echo "logs de odoo"
	docker compose logs -f $(CONTAINER_WEB)
	@echo "logs de db"
	docker compose logs -f $(CONTAINER_DB)
	
rebuild: 
	docker compose down 
	docker compose up -d

restart:
	docker compose restart

upgrade:
	docker exec odoo-web-1 odoo -u ventas_custom -d aaaaaaaaaaaaaaa --stop-after-init