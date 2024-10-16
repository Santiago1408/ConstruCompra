SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


CREATE TABLE `productos` (
  `id_producto` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL, 
  `descripcion` varchar(500) DEFAULT NULL, 
  `cantidad` int(11) DEFAULT NULL, 
  `precio` decimal(10,2) NOT NULL, 
  `ubicacion` varchar(500) NOT NULL, 
  `tamano` varchar(50) DEFAULT NULL, 
  `fecha_publicacion` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  PRIMARY KEY (`id_producto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
