SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";



CREATE TABLE `productos` (
  `id_producto` int(11) NOT NULL AUTO_INCREMENT,
  `id_usuarios` int(11) NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `descripcion` varchar(500) DEFAULT NULL,
  `cantidad` int(11) DEFAULT NULL,
  `tipo_venta` enum('Unitario','Total') NOT NULL,
  `precio` decimal(10,2) NOT NULL,
  `ubicacion` varchar(500) NOT NULL,
  `marca` varchar(100) DEFAULT NULL,
  `color` varchar(50) DEFAULT NULL,
  `tamano` varchar(50) DEFAULT NULL,
  `fecha_publicacion` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  PRIMARY KEY (`id_producto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


INSERT INTO `productos` (`id_producto`, `id_usuarios`, `nombre`, `descripcion`, `cantidad`, `tipo_venta`, `precio`, `ubicacion`, `marca`, `color`, `tamano`, `fecha_publicacion`) VALUES
(1, 4, 'Cemento', 'Bolsa de cemento Portland de 50kg', 100, 'Total', 45.50, 'Calle 123, Cochabamba', 'Fancesa', 'Gris', '50kg', '2024-10-05 00:47:51'),
(2, 4, 'Ladrillos', 'Ladrillos tipo King Kong 18x18x33 cm', 500, 'Unitario', 1.20, 'Av. Libertad 456, Cochabamba', 'Ladrix', 'Rojo', '18x18x33 cm', '2024-10-05 00:47:51'),
(3, 5, 'Arena', 'Metro cúbico de arena fina para construcción', 10, 'Total', 35.00, 'Calle de los Álamos 789, Cochabamba', NULL, 'Amarillo', '1 m3', '2024-10-05 00:47:51'),
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

--
--Estructura de tabla para almacenar imagenes de los producto
--
CREATE TABLE `imagenes_productos` (
    `id_imagen` int(11) NOT NULL AUTO_INCREMENT,
    `id_producto` int(11) NOT NULL,
    `url_imagen` varchar(255) NOT NULL CHECK (`url_imagen` <> ''),
    PRIMARY KEY (`id_imagen`),
    FOREIGN KEY (`id_producto`) REFERENCES `productos`(`id_producto`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
---------------------------------------------------------------


CREATE TABLE `usuarios` (
  `id_usuarios` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `fecha_nacimiento` date NOT NULL,
  `genero` enum('Masculino', 'Femenino', 'Otro') NOT NULL,
  `direccion` varchar(100) DEFAULT NULL,
  `telefono` varchar(15) DEFAULT NULL,
  `correo` varchar(100) NOT NULL,
  `contrasenia` varchar(255) NOT NULL,
  `foto_perfil` BLOB DEFAULT NULL,
  PRIMARY KEY (`id_usuarios`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;




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
