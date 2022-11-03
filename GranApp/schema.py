#Querys a ejecutar.
instructions = [
    #'SET FOREIGN_KEY_CHECKS=0; ', #Nos permite eliminar tablas con valores foraneos.
    'DROP TABLE IF EXISTS todo;', #Eliminar tablas si es que existen
    'DROP TABLE IF EXISTS usuario;',
    'DROP TABLE IF EXISTS admin;',
    'DROP TABLE IF EXISTS email;',
    #'SET FOREIGN_KEY_CHECKS=1',
    """
        CREATE TABLE usuario (        
            id INT PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(250) NOT NULL,
            email VARCHAR(75) UNIQUE NOT NULL   
        )
    """, 
    """
        CREATE TABLE todo (
            id INT PRIMARY KEY AUTO_INCREMENT,
            created_by INT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            description TEXT NOT NULL,
            completed BOOLEAN NOT NULL,
            completed_at TIMESTAMP,
            KEY created_by_idx (created_by)  
        ) 
    """,     #Asignamos la columna que recibe referencias de datos foraneos.
    """
        CREATE TABLE `admin` (
        `id` int NOT NULL AUTO_INCREMENT,
        `aname` varchar(25) NOT NULL,
        `apassword` varchar(250) NOT NULL,
        PRIMARY KEY (`id`),
        UNIQUE KEY `aname` (`aname`)
        ) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
    """,
    """ 
        CREATE TABLE `email` (
            `id` int NOT NULL AUTO_INCREMENT,
            `email` text NOT NULL,
            `subject` text NOT NULL,
            `content` text NOT NULL,
            PRIMARY KEY (`id`)
        ) ENGINE InnoDB,
        CHARSET utf8mb4,
        COLLATE utf8mb4_0900_ai_ci;
    """
]