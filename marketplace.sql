-- phpMyAdmin SQL Dump
-- version 6.0.0-dev
-- https://www.phpmyadmin.net/
--
-- Servidor: 192.168.30.22
-- Tiempo de generación: 05-10-2024 a las 00:48:04
-- Versión del servidor: 10.4.8-MariaDB-1:10.4.8+maria~stretch-log
-- Versión de PHP: 8.2.20

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `marketplace`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `productos`
--

CREATE TABLE `productos` (
  `id_producto` int(11) NOT NULL AUTO_INCREMENT,
  `id_usuarios` int(11) NOT NULL,
  `nombre` varchar(25) NOT NULL,
  `descripcion` varchar(100) DEFAULT NULL,
  `cantidad` int(11) DEFAULT NULL,
  `tipo_venta` enum('Unitario','Total') NOT NULL,
  `precio` decimal(10,2) NOT NULL,
  `ubicacion` varchar(255) NOT NULL,
  `marca` varchar(50) DEFAULT NULL,
  `color` varchar(50) DEFAULT NULL,
  `tamano` varchar(50) DEFAULT NULL,
  `fecha_publicacion` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  PRIMARY KEY (`id_producto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


--
-- Volcado de datos para la tabla `productos`
--

INSERT INTO `productos` (`id_producto`, `id_usuarios`, `nombre`, `descripcion`, `cantidad`, `tipo_venta`, `precio`, `ubicacion`, `marca`, `color`, `tamano`, `fecha_publicacion`) VALUES
(1, 1, 'Cemento', 'Bolsa de cemento Portland de 50kg', 100, 'Total', 45.50, 'Calle 123, Cochabamba', 'Fancesa', 'Gris', '50kg', '2024-10-05 00:47:51'),
(2, 2, 'Ladrillos', 'Ladrillos tipo King Kong 18x18x33 cm', 500, 'Unitario', 1.20, 'Av. Libertad 456, Cochabamba', 'Ladrix', 'Rojo', '18x18x33 cm', '2024-10-05 00:47:51'),
(3, 3, 'Arena', 'Metro cúbico de arena fina para construcción', 10, 'Total', 35.00, 'Calle de los Álamos 789, Cochabamba', NULL, 'Amarillo', '1 m3', '2024-10-05 00:47:51'),
(4, 4, 'Pintura acrílica', 'Galón de pintura acrílica blanca', 50, 'Unitario', 75.00, 'Av. América 321, Cochabamba', 'Sipa', 'Blanco', '1 galón', '2024-10-05 00:47:51'),
(5, 5, 'Varilla de acero', 'Varilla de acero corrugado de 12mm', 200, 'Unitario', 25.00, 'Av. Melchor Pérez 654, Cochabamba', 'Acerbol', 'Plateado', '12mm', '2024-10-05 00:47:51'),
(6, 6, 'Azulejos', 'Paquete de 1m2 de azulejos cerámicos', 50, 'Total', 120.00, 'Calle Tiquipaya 135, Cochabamba', 'Keramia', 'Blanco', '1m2', '2024-10-05 00:47:51'),
(7, 7, 'Grava', 'Metro cúbico de grava gruesa', 15, 'Total', 40.00, 'Av. Blanco Galindo 246, Cochabamba', NULL, 'Gris', '1 m3', '2024-10-05 00:47:51'),
(8, 8, 'Puerta de madera', 'Puerta de madera maciza de 2x0.8m', 20, 'Unitario', 250.00, 'Calle Aranjuez 357, Cochabamba', 'Maderco', 'Marrón', '2x0.8m', '2024-10-05 00:47:51'),
(9, 9, 'Tejas', 'Tejas cerámicas para techos', 300, 'Unitario', 5.00, 'Av. Beijing 468, Cochabamba', 'CeramTec', 'Rojo', '30x30cm', '2024-10-05 00:47:51'),
(10, 10, 'Tubería PVC', 'Tubería PVC de 4 pulgadas', 100, 'Total', 30.00, 'Calle Cobija 579, Cochabamba', 'Plastibol', 'Blanco', '4 pulgadas', '2024-10-05 00:47:51'),
(11, 11, 'Malla electrosoldada', 'Malla electrosoldada de 6x6mm', 50, 'Unitario', 100.00, 'Av. Circunvalación 680, Cochabamba', 'Metaldom', 'Plateado', '6x6mm', '2024-10-05 00:47:51'),
(12, 12, 'Ventana de aluminio', 'Ventana de aluminio de 1.2x1m', 25, 'Unitario', 150.00, 'Av. Villazón 791, Cochabamba', 'Alumco', 'Gris', '1.2x1m', '2024-10-05 00:47:51'),
(13, 13, 'Yeso', 'Bolsa de yeso de 25kg', 80, 'Total', 30.00, 'Calle Lanza 902, Cochabamba', 'YesBol', 'Blanco', '25kg', '2024-10-05 00:47:51'),
(14, 14, 'Cal', 'Bolsa de cal de 30kg', 60, 'Total', 35.00, 'Av. Salamanca 135, Cochabamba', 'Fancesa', 'Blanco', '30kg', '2024-10-05 00:47:51'),
(15, 15, 'Grifería', 'Juego de grifería cromada para baño', 40, 'Unitario', 200.00, 'Calle Tomás Frías 246, Cochabamba', 'Grifor', 'Plateado', 'Estándar', '2024-10-05 00:47:51'),
(16, 16, 'Lámina de yeso', 'Lámina de yeso de 2.4x1.2m', 100, 'Unitario', 80.00, 'Calle Mairana 357, Cochabamba', 'YesCoch', 'Blanco', '2.4x1.2m', '2024-10-05 00:47:51'),
(17, 17, 'Cemento cola', 'Bolsa de cemento cola para cerámica', 150, 'Total', 45.00, 'Av. Petrolera 468, Cochabamba', 'AdhesBol', 'Gris', '25kg', '2024-10-05 00:47:51'),
(18, 18, 'Luminaria LED', 'Lámpara LED de techo 18W', 75, 'Unitario', 60.00, 'Calle Jordan 579, Cochabamba', 'LumiTec', 'Blanco', '18W', '2024-10-05 00:47:51'),
(19, 19, 'Piso flotante', 'Paquete de 2m2 de piso flotante', 25, 'Total', 300.00, 'Calle España 680, Cochabamba', 'PisoFlex', 'Madera', '2m2', '2024-10-05 00:47:51'),
(20, 20, 'Interruptor eléctrico', 'Interruptor eléctrico de pared', 100, 'Unitario', 20.00, 'Av. América Oeste 791, Cochabamba', 'Elec', 'Blanco', '15 cm', '2024-10-05 00:47:51');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id_usuarios` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `fecha_nacimiento` date NOT NULL,
  `genero` enum('Masculino', 'Femenino', 'Otro') NOT NULL,
  `direccion` varchar(100) DEFAULT NULL,
  `telefono` varchar(15) DEFAULT NULL,
  `correo` varchar(100) NOT NULL,
  `contrasenia` varchar(255) NOT NULL,
  PRIMARY KEY (`id_usuarios`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;



--
-- Volcado de datos para la tabla `usuarios` con números de teléfono
--

INSERT INTO `usuarios` (`id_usuarios`, `nombre`, `fecha_nacimiento`, `genero`, `direccion`, `telefono`, `correo`, `contrasenia`) VALUES
(4, 'Sofía Morales', '1992-04-15', 'Femenino', 'Av. América 321, Cochabamba', '74845678', 'sofia.morales@outlook.com', 'password123'),
(5, 'José Sánchez', '1989-09-30', 'Masculino', 'Av. Melchor Pérez 654, Cochabamba', '71656789', 'jose.sanchez@live.com', 'password123'),
(6, 'Ana Gómez', '1995-11-20', 'Femenino', 'Calle Tiquipaya 135, Cochabamba', '71267890', 'ana.gomez@gmail.com', 'password123'),
(7, 'Pedro Ramírez', '1990-07-10', 'Masculino', 'Av. Blanco Galindo 246, Cochabamba', '71178901', 'pedro.ramirez@hotmail.com', 'password123'),
(8, 'María Vargas', '1988-03-22', 'Femenino', 'Calle Aranjuez 357, Cochabamba', '72289012', 'maria.vargas@yahoo.com', 'password123'),
(9, 'Fernando Ruiz', '1993-05-17', 'Masculino', 'Av. Beijing 468, Cochabamba', '79990123', 'fernando.ruiz@outlook.com', 'password123'),
(10, 'Julia López', '1996-02-08', 'Femenino', 'Calle Cobija 579, Cochabamba', '72801234', 'julia.lopez@gmail.com', 'password123'),
(11, 'Ricardo Martínez', '1987-06-25', 'Masculino', 'Av. Circunvalación 680, Cochabamba', '72512345', 'ricardo.martinez@yahoo.com', 'password123'),
(12, 'Patricia Herrera', '1994-12-01', 'Femenino', 'Av. Villazón 791, Cochabamba', '74423456', 'patricia.herrera@outlook.com', 'password123'),
(13, 'Manuel Gutiérrez', '1991-08-18', 'Masculino', 'Calle Lanza 902, Cochabamba', '72134567', 'manuel.gutierrez@gmail.com', 'password123'),
(14, 'Lucía Castro', '1990-10-05', 'Femenino', 'Av. Salamanca 135, Cochabamba', '73345678', 'lucia.castro@hotmail.com', 'password123'),
(15, 'Raúl Ortiz', '1985-01-14', 'Masculino', 'Calle Tomás Frías 246, Cochabamba', '73556789', 'raul.ortiz@yahoo.com', 'password123'),
(16, 'Valeria Jiménez', '1992-07-25', 'Femenino', 'Calle Mairana 357, Cochabamba', '71267890', 'valeria.jimenez@outlook.com', 'password123'),
(17, 'Gustavo Salazar', '1989-11-11', 'Masculino', 'Av. Petrolera 468, Cochabamba', '72778901', 'gustavo.salazar@gmail.com', 'password123'),
(18, 'Mónica Muñoz', '1995-03-07', 'Femenino', 'Calle Jordan 579, Cochabamba', '73489012', 'monica.munoz@hotmail.com', 'password123'),
(19, 'Sebastián Rojas', '1988-05-14', 'Masculino', 'Calle España 680, Cochabamba', '72390123', 'sebastian.rojas@outlook.com', 'password123'),
(20, 'Claudia Paredes', '1994-09-22', 'Femenino', 'Av. América Oeste 791, Cochabamba', '74301234', 'claudia.paredes@yahoo.com', 'password123'),
(21, 'Diego Espinoza', '1990-12-30', 'Masculino', 'Calle Aroma 902, Cochabamba', '75412345', 'diego.espinoza@hotmail.com', 'password123'),
(22, 'Elena Suárez', '1991-06-19', 'Femenino', 'Calle Sucre 135, Cochabamba', '76623456', 'elena.suarez@gmail.com', 'password123'),
(23, 'Rodrigo Medina', '1992-02-03', 'Masculino', 'Calle 25 de Mayo 246, Cochabamba', '77834567', 'rodrigo.medina@yahoo.com', 'password123'),
(24, 'Cecilia Villarroel', '1986-11-09', 'Femenino', 'Av. Oquendo 357, Cochabamba', '79045678', 'cecilia.villarroel@outlook.com', 'password123'),
(25, 'Andrés Álvarez', '1993-04-12', 'Masculino', 'Calle Punata 468, Cochabamba', '79956789', 'andres.alvarez@gmail.com', 'password123');

-- Indices de la tabla `productos`
--
ALTER TABLE `productos`
  ADD PRIMARY KEY (`id_producto`),
  ADD KEY `id_usuarios` (`id_usuarios`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id_usuarios`),
  ADD UNIQUE KEY `correo` (`correo`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `productos`
--
ALTER TABLE `productos`
  MODIFY `id_producto` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id_usuarios` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=26;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `productos`
--
ALTER TABLE `productos`
  ADD CONSTRAINT `productos_ibfk_1` FOREIGN KEY (`id_usuarios`) REFERENCES `usuarios` (`id_usuarios`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
