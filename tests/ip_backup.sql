-- phpMyAdmin SQL Dump
-- version 3.4.11.1deb2+deb7u1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Dec 05, 2015 at 09:47 AM
-- Server version: 5.5.43
-- PHP Version: 5.4.41-0+deb7u1

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `ip`
--
CREATE DATABASE `ip` DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;
USE `ip`;

-- --------------------------------------------------------

--
-- Table structure for table `arbeitsplan`
--

CREATE TABLE IF NOT EXISTS `arbeitsplan` (
  `ID` int(6) NOT NULL AUTO_INCREMENT,
  `Artikelnummer` int(6) NOT NULL,
  `Position` int(3) DEFAULT NULL,
  `AV_Nummer` int(6) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1000000 ;

--
-- Dumping data for table `arbeitsplan`
--

INSERT INTO `arbeitsplan` (`ID`, `Artikelnummer`, `Position`, `AV_Nummer`) VALUES
(2001, 5341, 1, 2001),
(1001, 500, 1, 1001),
(3001, 4202, 1, 3001),
(4001, 31, 1, 4001),
(5001, 5890, 1, 5001),
(5002, 5891, 1, 5002),
(6002, 20, 1, 6001);

-- --------------------------------------------------------

--
-- Table structure for table `arbeitsvorgang`
--

CREATE TABLE IF NOT EXISTS `arbeitsvorgang` (
  `AV_Nummer` int(6) NOT NULL AUTO_INCREMENT,
  `AV_Beschreibung` varchar(48) DEFAULT NULL,
  `AV_Zykluszeit` int(6) DEFAULT NULL,
  `FM_Nummer` int(6) DEFAULT NULL,
  `AV_Art` varchar(3) DEFAULT NULL,
  PRIMARY KEY (`AV_Nummer`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1000000 ;

--
-- Dumping data for table `arbeitsvorgang`
--

INSERT INTO `arbeitsvorgang` (`AV_Nummer`, `AV_Beschreibung`, `AV_Zykluszeit`, `FM_Nummer`, `AV_Art`) VALUES
(1001, 'UB fraesen', 300, 808080, 'fr1'),
(2001, 'Motor einbau', 600, 707070, 'mn1'),
(3001, 'blau lackieren', 300, 606060, 'lk1'),
(4001, 'akku einbauen', 300, 707070, 'mn1'),
(5001, 'winterreifen', 300, 505050, 'dr1'),
(5002, 'sommerreifen', 300, 505050, 'dr1'),
(6001, 'chassie drucken', 18000, 404040, 'pr1');

-- --------------------------------------------------------

--
-- Table structure for table `artikel`
--

CREATE TABLE IF NOT EXISTS `artikel` (
  `Artikelnummer` int(6) NOT NULL AUTO_INCREMENT,
  `Beschreibung` varchar(35) DEFAULT NULL,
  `Mindestbestand` int(6) DEFAULT NULL,
  `Los` int(6) DEFAULT NULL,
  `Artikelart` varchar(3) DEFAULT NULL,
  `Artikelkategorie` varchar(2) NOT NULL,
  `Mutterkategorie` tinyint(1) NOT NULL,
  PRIMARY KEY (`Artikelnummer`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1000000 ;

--
-- Dumping data for table `artikel`
--

INSERT INTO `artikel` (`Artikelnummer`, `Beschreibung`, `Mindestbestand`, `Los`, `Artikelart`, `Artikelkategorie`, `Mutterkategorie`) VALUES
(20, 'plastik', NULL, NULL, NULL, 'km', 0),
(500, 'A5', NULL, NULL, NULL, 'ch', 0),
(501, 'A5', NULL, NULL, NULL, 'ch', 0),
(4201, 'rot', NULL, NULL, NULL, 'la', 0),
(4202, 'blau', NULL, NULL, NULL, 'la', 0),
(21, 'metall', NULL, NULL, NULL, 'km', 0),
(5340, 'Antriebsmotor_Servo', NULL, NULL, NULL, 'ma', 0),
(5341, 'Antriebsmotor_Schritt', NULL, NULL, NULL, 'ma', 0),
(5440, 'Lenkmotor_Servo', NULL, NULL, NULL, 'ml', 0),
(5441, 'Lenkmotor_Schritt', NULL, NULL, NULL, 'ml', 0),
(30, 'Batterien', NULL, NULL, NULL, 'ev', 0),
(31, 'Akkus', NULL, NULL, NULL, 'ev', 0),
(5890, 'Winterreifen', NULL, NULL, NULL, 'rv', 0),
(5891, 'Sommerreifen', NULL, NULL, NULL, 'rv', 0),
(5990, 'Winterreifen', NULL, NULL, NULL, 'rh', 0),
(5991, 'Sommerreifen', NULL, NULL, NULL, 'rh', 0);

-- --------------------------------------------------------

--
-- Table structure for table `bom`
--

CREATE TABLE IF NOT EXISTS `bom` (
  `ID` int(6) NOT NULL AUTO_INCREMENT,
  `Baugruppe` varchar(6) NOT NULL,
  `Bauteil` varchar(6) NOT NULL,
  `SL_Menge` int(6) NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1000000 ;

--
-- Dumping data for table `bom`
--

INSERT INTO `bom` (`ID`, `Baugruppe`, `Bauteil`, `SL_Menge`) VALUES
(999999, '99', '99', 999999);

-- --------------------------------------------------------

--
-- Table structure for table `fertigungsmittel`
--

CREATE TABLE IF NOT EXISTS `fertigungsmittel` (
  `FM_Nummer` int(6) NOT NULL AUTO_INCREMENT,
  `Artikelnummer` int(6) DEFAULT NULL,
  `FM_Zeit` int(6) DEFAULT NULL,
  `FM_Kategorie` varchar(3) DEFAULT NULL,
  PRIMARY KEY (`FM_Nummer`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1000000 ;

--
-- Dumping data for table `fertigungsmittel`
--

INSERT INTO `fertigungsmittel` (`FM_Nummer`, `Artikelnummer`, `FM_Zeit`, `FM_Kategorie`) VALUES
(999999, 999999, 999999, 'AAA'),
(505050, 5890, 300, 'dr1');

-- --------------------------------------------------------

--
-- Table structure for table `kunde`
--

CREATE TABLE IF NOT EXISTS `kunde` (
  `KN_Nummer` int(6) NOT NULL AUTO_INCREMENT,
  `KN_Name` varchar(22) DEFAULT NULL,
  `KN_Bewertung` varchar(1) DEFAULT NULL,
  PRIMARY KEY (`KN_Nummer`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1000000 ;

--
-- Dumping data for table `kunde`
--

INSERT INTO `kunde` (`KN_Nummer`, `KN_Name`, `KN_Bewertung`) VALUES
(999999, 'JuliaBelke', 'A'),
(575777, 'AlexanderPoehler', 'B');

-- --------------------------------------------------------

--
-- Table structure for table `kundenauftrag`
--

CREATE TABLE IF NOT EXISTS `kundenauftrag` (
  `KA_Nummer` int(6) NOT NULL AUTO_INCREMENT,
  `KN_Nummer` int(6) DEFAULT NULL,
  `KA_Termin` date DEFAULT NULL,
  `KA_Kategorie` varchar(1) DEFAULT NULL,
  `KA_Status` int(2) NOT NULL,
  `KA_Prio` int(6) DEFAULT NULL,
  `UB` int(6) DEFAULT NULL,
  `UBst` int(1) NOT NULL,
  `MO` int(6) DEFAULT NULL,
  `LA` int(6) DEFAULT NULL,
  `EV` int(6) DEFAULT NULL,
  `RF` int(6) DEFAULT NULL,
  `RFst` int(1) NOT NULL,
  `CH` int(6) DEFAULT NULL,
  `CHst` int(1) NOT NULL,
  PRIMARY KEY (`KA_Nummer`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1000028 ;

--
-- Dumping data for table `kundenauftrag`
--

INSERT INTO `kundenauftrag` (`KA_Nummer`, `KN_Nummer`, `KA_Termin`, `KA_Kategorie`, `KA_Status`, `KA_Prio`, `UB`, `UBst`, `MO`, `LA`, `EV`, `RF`, `RFst`, `CH`, `CHst`) VALUES
(1000022, 156567, NULL, 'I', 0, 1, 1001, 0, 2001, 3001, 4001, 5001, 0, 6001, 0),
(1000021, 112125, NULL, 'K', 0, 1, 1001, 0, 2001, 3001, 4001, 5001, 0, 6001, 0),
(1000016, 100000, NULL, 'I', 3, 1, 1001, 0, 2001, 3001, 4001, 5001, 0, 6001, 0),
(1000020, 100097, NULL, 'K', 2, 1, 1001, 0, 2001, 3001, 4001, 5001, 0, 6001, 0),
(1000019, 197355, NULL, 'K', 0, 2, 1001, 0, 2001, 3001, 4001, 5001, 0, 6001, 0),
(1000018, 166665, NULL, 'K', 2, 2, 1001, 0, 2001, 3001, 4001, 5001, 0, 6001, 0),
(1000017, 145645, NULL, 'K', 0, 1, 1001, 0, 2001, 3001, 4001, 5001, 0, 6001, 0),
(1000023, 563467, NULL, 'I', 0, 1, 1001, 0, 2001, 3001, 4001, 5001, 0, 6001, 0),
(1000024, 975143, NULL, 'I', 0, 1, 1001, 0, 2001, 3001, 4001, 5001, 0, 6001, 0),
(1000025, 975143, NULL, 'I', 0, 1, 1001, 0, 2001, 3001, 4001, 5002, 0, 6001, 0),
(1000026, 945642, NULL, 'I', 0, 1, 1001, 0, 2001, 3001, 4001, 5002, 0, 6001, 0),
(1000027, 998877, NULL, 'K', 0, 1, 1001, 0, 2001, 3001, 4001, 5002, 0, 6001, 0);

-- --------------------------------------------------------

--
-- Table structure for table `lieferant`
--

CREATE TABLE IF NOT EXISTS `lieferant` (
  `LN_Nummer` int(6) NOT NULL AUTO_INCREMENT,
  `LN_Name` varchar(20) DEFAULT NULL,
  `LN_Bewertung` varchar(1) DEFAULT NULL,
  PRIMARY KEY (`LN_Nummer`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1000000 ;

--
-- Dumping data for table `lieferant`
--

INSERT INTO `lieferant` (`LN_Nummer`, `LN_Name`, `LN_Bewertung`) VALUES
(999999, 'AAAAAAAAAAAAAAAAAAAA', 'A');

-- --------------------------------------------------------

--
-- Table structure for table `lieferantenauftrag`
--

CREATE TABLE IF NOT EXISTS `lieferantenauftrag` (
  `LA_Nummer` int(6) NOT NULL AUTO_INCREMENT,
  `Artikelnummer` int(6) DEFAULT NULL,
  `LA_Menge` int(6) DEFAULT NULL,
  `LN_Nummer` int(6) DEFAULT NULL,
  `LA_Termin` int(5) DEFAULT NULL,
  `LA_Kategorie` varchar(1) DEFAULT NULL,
  PRIMARY KEY (`LA_Nummer`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1000000 ;

--
-- Dumping data for table `lieferantenauftrag`
--

INSERT INTO `lieferantenauftrag` (`LA_Nummer`, `Artikelnummer`, `LA_Menge`, `LN_Nummer`, `LA_Termin`, `LA_Kategorie`) VALUES
(999999, 999999, 999999, 999999, 42370, 'A');

-- --------------------------------------------------------

--
-- Table structure for table `materialbuchung`
--

CREATE TABLE IF NOT EXISTS `materialbuchung` (
  `ID` int(6) NOT NULL AUTO_INCREMENT,
  `artikelnummer` int(6) NOT NULL,
  `buchungsmenge` int(6) NOT NULL,
  `LPZ_abgebend` varchar(3) DEFAULT NULL,
  `LPZ_aufnehmend` varchar(3) DEFAULT NULL,
  `buchungstyp` varchar(3) DEFAULT NULL,
  `buchungszeit` timestamp NULL DEFAULT NULL,
  `buchungskommentar` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `z_lieferanten_artikel`
--

CREATE TABLE IF NOT EXISTS `z_lieferanten_artikel` (
  `ID` int(6) NOT NULL AUTO_INCREMENT,
  `Artikelnummer` int(6) DEFAULT NULL,
  `LN_Nummer` int(6) DEFAULT NULL,
  `Mindestbestellmenge` int(6) DEFAULT NULL,
  `Wiederbeschaffungszeit` int(6) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1000000 ;

--
-- Dumping data for table `z_lieferanten_artikel`
--

INSERT INTO `z_lieferanten_artikel` (`ID`, `Artikelnummer`, `LN_Nummer`, `Mindestbestellmenge`, `Wiederbeschaffungszeit`) VALUES
(999999, 999999, 999999, 999999, 999999);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
