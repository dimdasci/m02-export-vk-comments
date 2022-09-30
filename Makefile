ARGS=--help

data_directory = "${CURDIR}/data"
image_tag = "1.0.0"
image_name = "vk_comments_export"
container_name = "vk_comments_export"

requirements:
	pip install -r requirements.txt

build:
	[ -d $(data_directory) ] || mkdir -p $(data_directory)
	docker build . -t ${image_name}:${image_tag} 

run:
	docker run \
		--name ${container_name} \
		--mount type=bind,source="${data_directory}",target=/home/dim/data \
		-it --rm ${image_name}:${image_tag} $(ARGS)
