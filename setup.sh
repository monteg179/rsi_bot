#!/bin/bash

COMPOSE=docker-compose.yml
OUT=setup.out
ERR=setup.err

docker_compose_build() {
    echo -n "Docker compose build ..."
    docker compose -f $COMPOSE build -q 1> $OUT 2>$ERR
    error=$?
    if [ $error -eq 0 ]; then
	    echo " completed"
    else
	    echo " error($error)"
    fi
    return $error
}

docker_compose_pull() {
    echo -n "Docker compose pull ..."
    docker compose -f $COMPOSE pull -q 1> $OUT 2>$ERR
    error=$?
    if [ $error -eq 0 ]; then
	    echo " completed"
    else
	    echo " error($error)"
    fi
    return $error
}

docker_compose_up() {
    echo -n "Docker compose up ..."
    docker compose -f $COMPOSE up -d --wait backend gateway 1> $OUT 2>$ERR
    error=$?
    if [ $error -eq 0 ]; then
	    echo " completed"
    else
	    echo " error($error)"
    fi
    return $error
}

docker_compose_down() {
    echo -n "Docker compose down ..."
    docker compose -f $COMPOSE down --rmi all 1> $OUT 2>$ERR
    error=$?
    if [ $error -eq 0 ]; then
	    echo " completed"
    else
	    echo " error($error)"
    fi
    return $error
}

docker_compose_remove() {
    echo -n "Docker compose remove ..."
    docker compose -f $COMPOSE down --rmi all -v 1> $OUT 2>$ERR
    error=$?
    if [ $error -eq 0 ]; then
	    echo " completed"
    else
	    echo " error($error)"
    fi
    return $error
}

docker_compose_init() {
    return 0
}

case "$1" in
	install)
        docker_compose_build && docker_compose_up && docker_compose_init
		if [ $? -ne 0 ]; then
			exit 1
		fi
		;;
	uninstall)
        docker_compose_remove
		if [ $? -ne 0 ]; then
			exit 1
		fi
		;;
	update)
        docker_compose_down && docker_compose_build && docker_compose_up
		if [ $? -ne 0 ]; then
			exit 1
		fi
		;;
    deploy)
		docker_compose_pull && docker_compose_up && docker_compose_init
		if [ $? -ne 0 ]; then
			exit 1
		fi
		;;
    *)
        echo "Usage: sudo bash $0 {install | uninstall | update | deploy}"
        exit 1
        ;;
esac

exit 0