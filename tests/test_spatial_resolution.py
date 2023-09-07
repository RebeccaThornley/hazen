import unittest
import pathlib
import pytest

import numpy as np
import os

from tests import TEST_DATA_DIR, TEST_REPORT_DIR
from hazenlib.tasks.spatial_resolution import SpatialResolution
from hazenlib.utils import get_dicom_files, rescale_to_byte


class TestSpatialResolution(unittest.TestCase):
    files = get_dicom_files(os.path.join(TEST_DATA_DIR, 'resolution', 'RESOLUTION'))
    TEST_SQUARE = [[300, 220], [219, 206], [205, 287], [286, 301]]
    CIRCLE = [[[254, 256, 197]]]
    CENTRE = {'x': 293, 'y': 260}  # of right edge
    TOP_CENTRE = {'x': 259, 'y': 213}
    signal_roi = [1568, 1565, 1574, 1575, 1559, 1568, 1562, 1565, 1566, 1566, 1576, 1574, 1558, 1563, 1559, 1566, 1566,
                  1576, 1563, 1569, 1575, 1572, 1579, 1582, 1568, 1571, 1578, 1577, 1569, 1574, 1581, 1589, 1567, 1581,
                  1583, 1569, 1584, 1585, 1578, 1591, 1593, 1586, 1571, 1590, 1581, 1578, 1577, 1591, 1578, 1584, 1593,
                  1587, 1577, 1574, 1581, 1586, 1574, 1580, 1584, 1599, 1579, 1579, 1591, 1576, 1586, 1580, 1588, 1586,
                  1582, 1589, 1603, 1567, 1595, 1602, 1593, 1596, 1587, 1598, 1596, 1590, 1615, 1596, 1590, 1596, 1590,
                  1596, 1595, 1594, 1596, 1600, 1605, 1608, 1612, 1586, 1588, 1592, 1593, 1604, 1621, 1601, 1612, 1600,
                  1605, 1614, 1609, 1611, 1605, 1600, 1602, 1610, 1602, 1603, 1610, 1599, 1606, 1604, 1618, 1619, 1621,
                  1616, 1616, 1616, 1620, 1608, 1617, 1602, 1605, 1612, 1612, 1623, 1612, 1612, 1604, 1631, 1626, 1617,
                  1617, 1612, 1605, 1626, 1624, 1598, 1615, 1612, 1618, 1617, 1617, 1624, 1634, 1618, 1623, 1626, 1634,
                  1636, 1627, 1632, 1629, 1632, 1638, 1616, 1627, 1624, 1632, 1627, 1626, 1640, 1632, 1628, 1637, 1634,
                  1629, 1643, 1634, 1638, 1636, 1638, 1625, 1640, 1642, 1636, 1646, 1627, 1629, 1639, 1630, 1626, 1629,
                  1651, 1634, 1640, 1636, 1639, 1636, 1650, 1646, 1658, 1652, 1649, 1653, 1656, 1634, 1647, 1639, 1645,
                  1649, 1640, 1638, 1658, 1645, 1645, 1647, 1653, 1653, 1662, 1644, 1648, 1657, 1662, 1658, 1651, 1665,
                  1651, 1654, 1648, 1652, 1655, 1658, 1651, 1651, 1656, 1664, 1658, 1672, 1671, 1671, 1664, 1660, 1661,
                  1668, 1672, 1671, 1665, 1668, 1654, 1659, 1647, 1657, 1667, 1665, 1656, 1673, 1682, 1676, 1660, 1667,
                  1678, 1672, 1670, 1661, 1663, 1665, 1671, 1674, 1670, 1679, 1669, 1669, 1673, 1680, 1671, 1673, 1675,
                  1693, 1686, 1684, 1688, 1690, 1681, 1692, 1683, 1684, 1669, 1671, 1683, 1680, 1685, 1679, 1681, 1686,
                  1695, 1698, 1700, 1694, 1679, 1679, 1688, 1688, 1686, 1695, 1695, 1695, 1704, 1695, 1690, 1689, 1689,
                  1694, 1701, 1687, 1687, 1699, 1699, 1704, 1697, 1700, 1692, 1708, 1708, 1712, 1712, 1716, 1707, 1710,
                  1717, 1704, 1704, 1683, 1711, 1691, 1699, 1710, 1709, 1709, 1713, 1713, 1714, 1712, 1711, 1717, 1711,
                  1702, 1708, 1713, 1705, 1714, 1721, 1712, 1706, 1736, 1718, 1705, 1710, 1718, 1726, 1726, 1721, 1726,
                  1731, 1727, 1735, 1735, 1732, 1736, 1738, 1735, 1739, 1721, 1721, 1742, 1739, 1737, 1728, 1720, 1726,
                  1731, 1733, 1724, 1737, 1727, 1736, 1728, 1724, 1727, 1741, 1738, 1737, 1741, 1745, 1727, 1715, 1726,
                  1735, 1747, 1750, 1737, 1736, 1747, 1755, 1758, 1751]
    void_roi = [5, 14, 16, 4, 17, 19, 7, 11, 10, 12, 14, 11, 11, 5, 24, 9, 21, 10, 10, 12, 12, 14, 7, 17, 10, 12, 17,
                19, 13, 14, 13, 9, 19, 12, 15, 9, 8, 12, 19, 17, 15, 6, 4, 23, 19, 5, 8, 19, 16, 5, 19, 5, 9, 6, 16, 12,
                8, 19, 7, 18, 15, 8, 9, 12, 11, 11, 12, 9, 18, 25, 4, 11, 5, 12, 11, 6, 6, 7, 14, 15, 10, 10, 8, 8, 17,
                13, 8, 30, 13, 5, 15, 17, 14, 8, 19, 8, 16, 25, 20, 15, 13, 9, 16, 11, 13, 4, 14, 29, 16, 15, 11, 11, 9,
                4, 11, 11, 10, 7, 6, 14, 10, 7, 17, 10, 9, 3, 14, 19, 22, 10, 15, 14, 10, 9, 4, 13, 24, 17, 9, 18, 13,
                7, 18, 9, 12, 18, 15, 11, 11, 14, 9, 13, 14, 13, 25, 12, 13, 9, 18, 19, 5, 14, 33, 11, 8, 8, 14, 11, 26,
                6, 8, 17, 7, 3, 12, 16, 11, 4, 17, 6, 17, 31, 12, 23, 21, 7, 6, 5, 14, 10, 13, 13, 13, 6, 17, 15, 18,
                21, 9, 10, 10, 10, 6, 12, 12, 13, 2, 6, 6, 11, 10, 23, 9, 14, 16, 8, 11, 24, 7, 10, 18, 9, 17, 23, 7,
                24, 9, 10, 10, 15, 8, 9, 14, 12, 8, 13, 11, 12, 7, 19, 12, 20, 15, 5, 7, 5, 8, 17, 23, 6, 6, 7, 7, 14,
                23, 6, 12, 10, 11, 4, 22, 11, 20, 22, 23, 20, 19, 14, 29, 11, 10, 11, 11, 4, 6, 18, 20, 20, 24, 17, 10,
                15, 4, 17, 9, 4, 23, 10, 5, 9, 13, 16, 9, 17, 13, 23, 8, 11, 15, 8, 11, 4, 23, 22, 14, 8, 10, 8, 11, 18,
                23, 19, 12, 3, 12, 11, 7, 6, 11, 11, 15, 12, 13, 16, 7, 18, 10, 17, 14, 23, 17, 8, 18, 10, 15, 8, 5, 3,
                12, 13, 10, 9, 22, 7, 5, 12, 13, 9, 9, 30, 17, 11, 22, 14, 11, 4, 7, 10, 26, 8, 24, 17, 11, 7, 7, 16,
                16, 5, 5, 14, 16, 7, 14, 19, 11, 5, 3, 10, 18, 13, 12, 13, 9, 15, 8, 17, 3, 4, 19, 10, 14, 10, 10, 17,
                12, 8, 9, 11, 9, 12]
    edge_roi = [9, 11, 13, 18, 25, 4, 4, 15, 8, 17, 26, 23, 11, 11, 17, 9, 17, 21, 7, 3, 11, 10, 10, 10, 6, 10, 8, 7,
                14, 4, 6, 3, 5, 10, 12, 12, 10, 17, 9, 15, 18, 7, 21, 17, 15, 17, 12, 12, 24, 10, 17, 10, 18, 23, 10, 5,
                10, 14, 3, 7, 15, 7, 18, 3, 4, 15, 16, 8, 19, 25, 16, 15, 5, 10, 2, 18, 13, 12, 14, 13, 14, 3, 5, 16,
                15, 6, 11, 11, 12, 9, 14, 18, 14, 12, 3, 15, 11, 15, 7, 6, 16, 9, 5, 22, 17, 11, 22, 2, 8, 12, 13, 5, 5,
                15, 17, 16, 2, 12, 9, 12, 15, 8, 13, 13, 4, 12, 6, 6, 12, 5, 17, 13, 3, 2, 14, 12, 6, 25, 16, 12, 0, 16,
                17, 5, 18, 9, 10, 19, 8, 0, 12, 18, 11, 6, 20, 23, 18, 12, 5, 13, 20, 18, 15, 11, 16, 23, 8, 1, 8, 14,
                29, 19, 8, 12, 13, 10, 4, 5, 3, 17, 0, 11, 8, 31, 21, 41, 32, 15, 16, 16, 25, 21, 18, 10, 2, 25, 5, 24,
                6, 12, 0, 0, 0, 0, 0, 0, 0, 7, 2, 29, 39, 24, 14, 25, 21, 11, 14, 18, 3, 2, 0, 0, 0, 0, 0, 0, 4, 6, 4,
                0, 0, 0, 0, 0, 6, 0, 23, 44, 35, 16, 106, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1240,
                1113, 923, 725, 520, 314, 143, 18, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1201, 1255, 1295, 1317, 1329,
                1306, 1242, 1138, 958, 751, 545, 356, 183, 33, 0, 0, 0, 0, 0, 0, 1160, 1136, 1125, 1116, 1126, 1165,
                1196, 1244, 1298, 1332, 1334, 1308, 1261, 1179, 1020, 813, 606, 407, 217, 60, 1147, 1167, 1169, 1179,
                1180, 1178, 1167, 1145, 1128, 1120, 1132, 1156, 1184, 1232, 1281, 1311, 1326, 1329, 1290, 1197, 1115,
                1118, 1114, 1108, 1116, 1115, 1137, 1160, 1179, 1188, 1195, 1200, 1187, 1162, 1144, 1137, 1131, 1147,
                1187, 1240, 1109, 1147, 1153, 1143, 1157, 1147, 1141, 1122, 1113, 1113, 1105, 1120, 1130, 1150, 1169,
                1184, 1196, 1191, 1181, 1168, 1141, 1139, 1131, 1132, 1127, 1139, 1126, 1139, 1127, 1148, 1133, 1146,
                1129, 1107, 1119, 1121, 1117, 1114, 1130, 1158]
    rotated_edge_roi = [1141, 1109, 1115, 1147, 1160, 1201, 1240, 106, 0, 0, 0, 20, 0, 15, 16, 14, 15, 18, 11, 9, 1139,
                        1147, 1118, 1167, 1136, 1255, 1113, 0, 0, 0, 11, 18, 16, 8, 9, 3, 7, 7, 10, 11, 1131, 1153,
                        1114, 1169, 1125, 1295, 923, 0, 0, 0, 8, 15, 17, 13, 5, 5, 18, 21, 10, 13, 1132, 1143, 1108,
                        1179, 1116, 1317, 725, 0, 0, 0, 31, 11, 5, 13, 22, 16, 3, 17, 10, 18, 1127, 1157, 1116, 1180,
                        1126, 1329, 520, 0, 0, 0, 21, 16, 18, 4, 17, 15, 4, 15, 6, 25, 1139, 1147, 1115, 1178, 1165,
                        1306, 314, 0, 0, 0, 41, 23, 9, 12, 11, 6, 15, 17, 10, 4, 1126, 1141, 1137, 1167, 1196, 1242,
                        143, 0, 4, 0, 32, 8, 10, 6, 22, 11, 16, 12, 8, 4, 1139, 1122, 1160, 1145, 1244, 1138, 18, 0, 6,
                        7, 15, 1, 19, 6, 2, 11, 8, 12, 7, 15, 1127, 1113, 1179, 1128, 1298, 958, 0, 0, 4, 2, 16, 8, 8,
                        12, 8, 12, 19, 24, 14, 8, 1148, 1113, 1188, 1120, 1332, 751, 0, 0, 0, 29, 16, 14, 0, 5, 12, 9,
                        25, 10, 4, 17, 1133, 1105, 1195, 1132, 1334, 545, 0, 0, 0, 39, 25, 29, 12, 17, 13, 14, 16, 17,
                        6, 26, 1146, 1120, 1200, 1156, 1308, 356, 0, 0, 0, 24, 21, 19, 18, 13, 5, 18, 15, 10, 3, 23,
                        1129, 1130, 1187, 1184, 1261, 183, 0, 0, 0, 14, 18, 8, 11, 3, 5, 14, 5, 18, 5, 11, 1107, 1150,
                        1162, 1232, 1179, 33, 0, 0, 0, 25, 10, 12, 6, 2, 15, 12, 10, 23, 10, 11, 1119, 1169, 1144, 1281,
                        1020, 0, 0, 0, 6, 21, 2, 13, 20, 14, 17, 3, 2, 10, 12, 17, 1121, 1184, 1137, 1311, 813, 0, 0, 0,
                        0, 11, 25, 10, 23, 12, 16, 15, 18, 5, 12, 9, 1117, 1196, 1131, 1326, 606, 0, 0, 0, 23, 14, 5, 4,
                        18, 6, 2, 11, 13, 10, 10, 17, 1114, 1191, 1147, 1329, 407, 0, 0, 0, 44, 18, 24, 5, 12, 25, 12,
                        15, 12, 14, 17, 21, 1130, 1181, 1187, 1290, 217, 0, 0, 0, 35, 3, 6, 3, 5, 16, 9, 7, 14, 3, 9, 7,
                        1158, 1168, 1240, 1197, 60, 0, 0, 0, 16, 2, 12, 17, 13, 12, 12, 6, 13, 7, 15, 3]
    x_edge = [0.0, 0.48828125, 0.9765625, 1.46484375, 1.953125, 2.44140625, 2.9296875, 3.41796875, 3.90625, 4.39453125,
              4.8828125, 5.37109375, 5.859375, 6.34765625, 6.8359375, 7.32421875, 7.8125, 8.30078125, 8.7890625,
              9.27734375]
    y_edge = [7.32421875, 7.32421875, 7.32421875, 7.32421875, 7.32421875, 6.8359375, 6.8359375, 6.8359375, 6.8359375,
              6.8359375, 6.8359375, 6.34765625, 6.34765625, 6.34765625, 6.34765625, 6.34765625, 6.34765625, 5.859375,
              5.859375, 5.859375]
    angle = -0.16392916582406125
    intercept = 8.091517857142858
    y = [-7.9830403532988505, -7.903354832530895, -7.823669311762939, -7.743983790994983, -7.664298270227027,
         -7.584612749459072, -7.504927228691115, -7.42524170792316, -7.3455561871552035, -7.265870666387248,
         -7.186185145619292, -7.106499624851336, -7.02681410408338, -6.947128583315425, -6.867443062547469,
         -6.787757541779513, -6.7080720210115565, -6.628386500243601, -6.548700979475646, -6.469015458707689,
         -7.501305159565299, -7.421619638797344, -7.341934118029387, -7.262248597261432, -7.182563076493476,
         -7.10287755572552, -7.023192034957564, -6.943506514189608, -6.863820993421652, -6.784135472653697,
         -6.70444995188574, -6.624764431117785, -6.545078910349829, -6.465393389581873, -6.385707868813917,
         -6.306022348045961, -6.226336827278006, -6.14665130651005, -6.066965785742093, -5.987280264974138,
         -7.019569965831748, -6.939884445063792, -6.860198924295836, -6.7805134035278805, -6.700827882759924,
         -6.621142361991969, -6.541456841224012, -6.461771320456057, -6.382085799688101, -6.302400278920145,
         -6.222714758152189, -6.1430292373842335, -6.063343716616277, -5.983658195848322, -5.903972675080366,
         -5.82428715431241, -5.744601633544454, -5.664916112776498, -5.585230592008543, -5.5055450712405865,
         -6.537834772098196, -6.458149251330241, -6.378463730562284, -6.298778209794329, -6.219092689026373,
         -6.139407168258417, -6.059721647490461, -5.9800361267225055, -5.900350605954549, -5.820665085186594,
         -5.740979564418637, -5.661294043650682, -5.581608522882726, -5.50192300211477, -5.422237481346814,
         -5.3425519605788585, -5.262866439810903, -5.183180919042947, -5.10349539827499, -5.023809877507035,
         -6.056099578364646, -5.97641405759669, -5.896728536828734, -5.8170430160607784, -5.737357495292822,
         -5.657671974524867, -5.57798645375691, -5.498300932988955, -5.418615412220999, -5.338929891453043,
         -5.259244370685087, -5.1795588499171314, -5.099873329149175, -5.02018780838122, -4.940502287613263,
         -4.860816766845308, -4.7811312460773525, -4.701445725309396, -4.62176020454144, -4.5420746837734844,
         -5.574364384631094, -5.494678863863139, -5.414993343095182, -5.335307822327227, -5.255622301559271,
         -5.175936780791315, -5.096251260023359, -5.0165657392554035, -4.936880218487447, -4.857194697719492,
         -4.777509176951535, -4.69782365618358, -4.618138135415624, -4.538452614647668, -4.458767093879713,
         -4.3790815731117565, -4.2993960523438, -4.219710531575845, -4.140025010807889, -4.060339490039933,
         -5.092629190897543, -5.012943670129587, -4.933258149361631, -4.8535726285936756, -4.773887107825719,
         -4.694201587057764, -4.6145160662898075, -4.534830545521852, -4.455145024753896, -4.37545950398594,
         -4.295773983217984, -4.2160884624500286, -4.136402941682072, -4.056717420914117, -3.977031900146161,
         -3.897346379378205, -3.817660858610249, -3.7379753378422933, -3.6582898170743374, -3.5786042963063815,
         -4.610893997163991, -4.531208476396036, -4.4515229556280795, -4.371837434860124, -4.292151914092168,
         -4.212466393324212, -4.132780872556256, -4.053095351788301, -3.9734098310203443, -3.893724310252389,
         -3.8140387894844325, -3.734353268716477, -3.6546677479485212, -3.5749822271805654, -3.4952967064126095,
         -3.4156111856446536, -3.3359256648766977, -3.256240144108742, -3.176554623340786, -3.09686910257283,
         -4.12915880343044, -4.049473282662484, -3.969787761894528, -3.890102241126572, -3.8104167203586163,
         -3.7307311995906605, -3.6510456788227046, -3.571360158054749, -3.491674637286793, -3.4119891165188374,
         -3.332303595750881, -3.2526180749829257, -3.17293255421497, -3.093247033447014, -3.013561512679058,
         -2.933875991911102, -2.8541904711431463, -2.7745049503751904, -2.6948194296072345, -2.6151339088392787,
         -3.647423609696889, -3.567738088928933, -3.488052568160977, -3.408367047393021, -3.3286815266250653,
         -3.2489960058571095, -3.1693104850891536, -3.0896249643211977, -3.0099394435532423, -2.930253922785286,
         -2.8505684020173305, -2.770882881249374, -2.6911973604814188, -2.6115118397134625, -2.531826318945507,
         -2.452140798177551, -2.3724552774095953, -2.2927697566416394, -2.2130842358736835, -2.1333987151057276,
         -3.1656884159633374, -3.0860028951953815, -3.0063173744274256, -2.9266318536594698, -2.846946332891514,
         -2.767260812123558, -2.687575291355602, -2.6078897705876463, -2.528204249819691, -2.4485187290517345,
         -2.368833208283779, -2.2891476875158228, -2.2094621667478673, -2.129776645979911, -2.0500911252119556,
         -1.9704056044439997, -1.8907200836760438, -1.811034562908088, -1.731349042140132, -1.6516635213721762,
         -2.6839532222297864, -2.6042677014618305, -2.5245821806938746, -2.4448966599259188, -2.365211139157963,
         -2.285525618390007, -2.205840097622051, -2.1261545768540957, -2.0464690560861394, -1.9667835353181837,
         -1.8870980145502279, -1.807412493782272, -1.7277269730143163, -1.6480414522463602, -1.5683559314784046,
         -1.4886704107104487, -1.4089848899424928, -1.329299369174537, -1.249613848406581, -1.1699283276386252,
         -2.202218028496235, -2.122532507728279, -2.042846986960323, -1.9631614661923673, -1.8834759454244114,
         -1.8037904246564556, -1.7241049038885, -1.644419383120544, -1.5647338623525882, -1.4850483415846323,
         -1.4053628208166764, -1.3256773000487205, -1.2459917792807649, -1.1663062585128088, -1.0866207377448531,
         -1.0069352169768973, -0.9272496962089414, -0.8475641754409855, -0.7678786546730296, -0.6881931339050738,
         -1.7204828347626837, -1.6407973139947278, -1.561111793226772, -1.481426272458816, -1.4017407516908604,
         -1.3220552309229046, -1.2423697101549487, -1.1626841893869928, -1.082998668619037, -1.003313147851081,
         -0.9236276270831252, -0.8439421063151693, -0.7642565855472135, -0.6845710647792576, -0.6048855440113019,
         -0.525200023243346, -0.44551450247539015, -0.3658289817074343, -0.2861434609394784, -0.20645794017152252,
         -1.2387476410291325, -1.1590621202611766, -1.0793765994932207, -0.999691078725265, -0.9200055579573091,
         -0.8403200371893532, -0.7606345164213975, -0.6809489956534416, -0.6012634748854857, -0.5215779541175298,
         -0.44189243334957395, -0.3622069125816181, -0.2825213918136623, -0.20283587104570633, -0.12315035027775068,
         -0.0434648295097948, 0.036220691258161075, 0.11590621202611695, 0.19559173279407283, 0.2752772535620287,
         -0.7570124472955811, -0.6773269265276253, -0.5976414057596695, -0.5179558849917136, -0.43827036422375776,
         -0.3585848434558019, -0.27889932268784606, -0.19921380191989024, -0.11952828115193437, -0.03984276038397849,
         0.03984276038397738, 0.11952828115193326, 0.19921380191988902, 0.278899322687845, 0.35858484345580066,
         0.43827036422375654, 0.5179558849917124, 0.5976414057596683, 0.6773269265276242, 0.75701244729558,
         -0.2752772535620298, -0.19559173279407396, -0.11590621202611812, -0.03622069125816227, 0.04346482950979358,
         0.12315035027774945, 0.20283587104570527, 0.2825213918136611, 0.36220691258161697, 0.44189243334957284,
         0.5215779541175287, 0.6012634748854846, 0.6809489956534404, 0.7606345164213963, 0.840320037189352,
         0.9200055579573079, 0.9996910787252637, 1.0793765994932196, 1.1590621202611755, 1.2387476410291314,
         0.20645794017152147, 0.2861434609394773, 0.36582898170743317, 0.44551450247538904, 0.5252000232433449,
         0.6048855440113008, 0.6845710647792566, 0.7642565855472123, 0.8439421063151682, 0.9236276270831241,
         1.00331314785108, 1.0829986686190358, 1.1626841893869917, 1.2423697101549476, 1.3220552309229032,
         1.401740751690859, 1.481426272458815, 1.5611117932267708, 1.6407973139947267, 1.7204828347626826,
         0.6881931339050728, 0.7678786546730286, 0.8475641754409844, 0.9272496962089403, 1.0069352169768961,
         1.086620737744852, 1.166306258512808, 1.2459917792807635, 1.3256773000487194, 1.4053628208166753,
         1.4850483415846312, 1.564733862352587, 1.644419383120543, 1.7241049038884988, 1.8037904246564547,
         1.8834759454244105, 1.9631614661923664, 2.0428469869603223, 2.122532507728278, 2.202218028496234,
         1.169928327638624, 1.24961384840658, 1.3292993691745358, 1.4089848899424917, 1.4886704107104474,
         1.5683559314784032, 1.6480414522463591, 1.727726973014315, 1.8074124937822709, 1.8870980145502267,
         1.9667835353181826, 2.0464690560861385, 2.1261545768540944, 2.2058400976220502, 2.2855256183900057,
         2.365211139157962, 2.4448966599259174, 2.5245821806938737, 2.604267701461829, 2.6839532222297855]
    x = [0.0, 0.48828125, 0.9765625, 1.46484375, 1.953125, 2.44140625, 2.9296875, 3.41796875, 3.90625, 4.39453125,
         4.8828125, 5.37109375, 5.859375, 6.34765625, 6.8359375, 7.32421875, 7.8125, 8.30078125, 8.7890625, 9.27734375,
         0.0, 0.48828125, 0.9765625, 1.46484375, 1.953125, 2.44140625, 2.9296875, 3.41796875, 3.90625, 4.39453125,
         4.8828125, 5.37109375, 5.859375, 6.34765625, 6.8359375, 7.32421875, 7.8125, 8.30078125, 8.7890625, 9.27734375,
         0.0, 0.48828125, 0.9765625, 1.46484375, 1.953125, 2.44140625, 2.9296875, 3.41796875, 3.90625, 4.39453125,
         4.8828125, 5.37109375, 5.859375, 6.34765625, 6.8359375, 7.32421875, 7.8125, 8.30078125, 8.7890625, 9.27734375,
         0.0, 0.48828125, 0.9765625, 1.46484375, 1.953125, 2.44140625, 2.9296875, 3.41796875, 3.90625, 4.39453125,
         4.8828125, 5.37109375, 5.859375, 6.34765625, 6.8359375, 7.32421875, 7.8125, 8.30078125, 8.7890625, 9.27734375,
         0.0, 0.48828125, 0.9765625, 1.46484375, 1.953125, 2.44140625, 2.9296875, 3.41796875, 3.90625, 4.39453125,
         4.8828125, 5.37109375, 5.859375, 6.34765625, 6.8359375, 7.32421875, 7.8125, 8.30078125, 8.7890625, 9.27734375,
         0.0, 0.48828125, 0.9765625, 1.46484375, 1.953125, 2.44140625, 2.9296875, 3.41796875, 3.90625, 4.39453125,
         4.8828125, 5.37109375, 5.859375, 6.34765625, 6.8359375, 7.32421875, 7.8125, 8.30078125, 8.7890625, 9.27734375,
         0.0, 0.48828125, 0.9765625, 1.46484375, 1.953125, 2.44140625, 2.9296875, 3.41796875, 3.90625, 4.39453125,
         4.8828125, 5.37109375, 5.859375, 6.34765625, 6.8359375, 7.32421875, 7.8125, 8.30078125, 8.7890625, 9.27734375,
         0.0, 0.48828125, 0.9765625, 1.46484375, 1.953125, 2.44140625, 2.9296875, 3.41796875, 3.90625, 4.39453125,
         4.8828125, 5.37109375, 5.859375, 6.34765625, 6.8359375, 7.32421875, 7.8125, 8.30078125, 8.7890625, 9.27734375,
         0.0, 0.48828125, 0.9765625, 1.46484375, 1.953125, 2.44140625, 2.9296875, 3.41796875, 3.90625, 4.39453125,
         4.8828125, 5.37109375, 5.859375, 6.34765625, 6.8359375, 7.32421875, 7.8125, 8.30078125, 8.7890625, 9.27734375,
         0.0, 0.48828125, 0.9765625, 1.46484375, 1.953125, 2.44140625, 2.9296875, 3.41796875, 3.90625, 4.39453125,
         4.8828125, 5.37109375, 5.859375, 6.34765625, 6.8359375, 7.32421875, 7.8125, 8.30078125, 8.7890625, 9.27734375,
         0.0, 0.48828125, 0.9765625, 1.46484375, 1.953125, 2.44140625, 2.9296875, 3.41796875, 3.90625, 4.39453125,
         4.8828125, 5.37109375, 5.859375, 6.34765625, 6.8359375, 7.32421875, 7.8125, 8.30078125, 8.7890625, 9.27734375,
         0.0, 0.48828125, 0.9765625, 1.46484375, 1.953125, 2.44140625, 2.9296875, 3.41796875, 3.90625, 4.39453125,
         4.8828125, 5.37109375, 5.859375, 6.34765625, 6.8359375, 7.32421875, 7.8125, 8.30078125, 8.7890625, 9.27734375,
         0.0, 0.48828125, 0.9765625, 1.46484375, 1.953125, 2.44140625, 2.9296875, 3.41796875, 3.90625, 4.39453125,
         4.8828125, 5.37109375, 5.859375, 6.34765625, 6.8359375, 7.32421875, 7.8125, 8.30078125, 8.7890625, 9.27734375,
         0.0, 0.48828125, 0.9765625, 1.46484375, 1.953125, 2.44140625, 2.9296875, 3.41796875, 3.90625, 4.39453125,
         4.8828125, 5.37109375, 5.859375, 6.34765625, 6.8359375, 7.32421875, 7.8125, 8.30078125, 8.7890625, 9.27734375,
         0.0, 0.48828125, 0.9765625, 1.46484375, 1.953125, 2.44140625, 2.9296875, 3.41796875, 3.90625, 4.39453125,
         4.8828125, 5.37109375, 5.859375, 6.34765625, 6.8359375, 7.32421875, 7.8125, 8.30078125, 8.7890625, 9.27734375,
         0.0, 0.48828125, 0.9765625, 1.46484375, 1.953125, 2.44140625, 2.9296875, 3.41796875, 3.90625, 4.39453125,
         4.8828125, 5.37109375, 5.859375, 6.34765625, 6.8359375, 7.32421875, 7.8125, 8.30078125, 8.7890625, 9.27734375,
         0.0, 0.48828125, 0.9765625, 1.46484375, 1.953125, 2.44140625, 2.9296875, 3.41796875, 3.90625, 4.39453125,
         4.8828125, 5.37109375, 5.859375, 6.34765625, 6.8359375, 7.32421875, 7.8125, 8.30078125, 8.7890625, 9.27734375,
         0.0, 0.48828125, 0.9765625, 1.46484375, 1.953125, 2.44140625, 2.9296875, 3.41796875, 3.90625, 4.39453125,
         4.8828125, 5.37109375, 5.859375, 6.34765625, 6.8359375, 7.32421875, 7.8125, 8.30078125, 8.7890625, 9.27734375,
         0.0, 0.48828125, 0.9765625, 1.46484375, 1.953125, 2.44140625, 2.9296875, 3.41796875, 3.90625, 4.39453125,
         4.8828125, 5.37109375, 5.859375, 6.34765625, 6.8359375, 7.32421875, 7.8125, 8.30078125, 8.7890625, 9.27734375,
         0.0, 0.48828125, 0.9765625, 1.46484375, 1.953125, 2.44140625, 2.9296875, 3.41796875, 3.90625, 4.39453125,
         4.8828125, 5.37109375, 5.859375, 6.34765625, 6.8359375, 7.32421875, 7.8125, 8.30078125, 8.7890625, 9.27734375]
    u = [-7.9830403532988505, -7.899048277900987, -7.815056202503124, -7.7310641271052605, -7.647072051707397,
         -7.563079976309535, -7.47908790091167, -7.395095825513808, -7.311103750115945, -7.227111674718081,
         -7.143119599320218, -7.0591275239223545, -6.975135448524491, -6.891143373126628, -6.8071512977287645,
         -6.723159222330901, -6.639167146933039, -6.555175071535174, -6.471182996137312, -6.387190920739449,
         -6.303198845341585, -6.219206769943722, -6.1352146945458585, -6.051222619147995, -5.967230543750132,
         -5.883238468352269, -5.799246392954405, -5.715254317556543, -5.631262242158678, -5.547270166760816,
         -5.463278091362953, -5.379286015965089, -5.295293940567226, -5.211301865169363, -5.127309789771499,
         -5.043317714373636, -4.959325638975773, -4.875333563577909, -4.791341488180047, -4.707349412782182,
         -4.62335733738432, -4.539365261986457, -4.455373186588593, -4.37138111119073, -4.287389035792867,
         -4.203396960395003, -4.11940488499714, -4.035412809599277, -3.951420734201413, -3.8674286588035507,
         -3.7834365834056873, -3.699444508007824, -3.6154524326099606, -3.5314603572120973, -3.447468281814234,
         -3.3634762064163706, -3.279484131018507, -3.195492055620644, -3.1114999802227805, -3.027507904824918,
         -2.9435158294270547, -2.8595237540291913, -2.775531678631328, -2.6915396032334646, -2.6075475278356013,
         -2.523555452437738, -2.4395633770398746, -2.3555713016420112, -2.271579226244148, -2.1875871508462845,
         -2.103595075448422, -2.0196030000505587, -1.9356109246526954, -1.851618849254832, -1.7676267738569686,
         -1.6836346984591053, -1.599642623061242, -1.5156505476633786, -1.4316584722655152, -1.3476663968676519,
         -1.2636743214697894, -1.179682246071926, -1.0956901706740627, -1.0116980952761994, -0.927706019878336,
         -0.8437139444804727, -0.7597218690826093, -0.675729793684746, -0.5917377182868826, -0.5077456428890192,
         -0.4237535674911559, -0.3397614920932934, -0.2557694166954301, -0.17177734129756672, -0.08778526589970337,
         -0.003793190501840016, 0.08019888489602423, 0.1641909602938867, 0.24818303569174915, 0.3321751110896134,
         0.41616718648747586, 0.5001592618853401, 0.5841513372832026, 0.6681434126810668, 0.7521354880789293,
         0.8361275634767935, 0.920119638874656, 1.0041117142725184, 1.0881037896703827, 1.1720958650682451,
         1.2560879404661094, 1.3400800158639719, 1.424072091261836, 1.5080641666596986, 1.5920562420575628,
         1.6760483174554253, 1.7600403928532895, 1.844032468251152, 1.9280245436490144, 2.0120166190468787,
         2.096008694444741, 2.1800007698426054, 2.263992845240468, 2.347984920638332, 2.4319769960361945,
         2.515969071434059, 2.5999611468319213, 2.6839532222297855]
    esf = [3.0, 7.756621331424564, 20.567644953471717, 15.702934860415121, 10.729420186113131, 15.37866857551899,
           13.831646044244446, 13.881889763779487, 20.6479190101237, 13.23359580052492, 9.925759280089995,
           13.72553430821147, 5.1598425196850375, 3.6728346456692993, 22.05511811023625, 16.33385826771654,
           11.80944881889758, 10.910629921259854, 9.125984251968525, 10.081889763779568, 14.574803149605513,
           17.748031496061508, 2.4629921259842305, 6.354330708661438, 8.267716535433175, 15.0, 12.474015748031546,
           16.830708661417283, 4.458267716535482, 14.362204724409413, 11.600787401574776, 8.056692913385866,
           2.552362204724411, 17.223622047244085, 10.287401574803207, 14.14960629921259, 8.598425196850481,
           17.00393700787394, 14.590551181102386, 5.570472440944814, 3.242519685039449, 19.984251968503845,
           12.874015748031276, 18.0251968503937, 21.81653543307095, 18.62283464566926, 16.858267716535437,
           4.746850393700706, 4.7464566929133865, 6.816929133858163, 11.117322834645638, 10.84055118110241,
           13.393700787401558, 7.502362204724395, 20.638582677165378, 5.0, 19.566929133858284, 12.340157480314941,
           0.42519685039370203, 19.149606299212355, 16.266141732283486, 11.220866141732316, 14.943307086614134,
           15.283464566929366, 15.98425196850041, 43.67401574803155, 23.588976377952743, 1.0645669291338524,
           6.962598425196851, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
           39.803149606297666, 219.13858267716503, 416.2090551181101, 622.7724409448819, 835.0433070866143,
           1044.1653543307077, 1209.1889763779523, 1295.259842519685, 1329.0, 1321.9712598425197, 1302.8866141732283,
           1266.2700787401575, 1216.354330708662, 1173.020472440945, 1132.4074803149608, 1119.6850393700788,
           1127.2346456692915, 1137.0141732283464, 1160.5669291338584, 1178.1736220472442, 1180.47244094488,
           1187.1181102362218, 1168.9590551181102, 1157.653543307087, 1128.6594488188978, 1114.2976377952755,
           1115.1255905511812, 1119.1259842519685, 1118.6728346456694, 1110.0929133858267, 1136.6467941507312,
           1151.2958380202474, 1138.3805774278214, 1150.973378327709, 1140.025871766029, 1117.7626546681665,
           1135.4871152469577, 1129.5941302791696, 1131.1893342877595, 1131.108088761632, 1138.5676449534717, 1141.0]
    lsf = [4.757, 8.784, 3.973, -4.919, -0.162, 1.551, -0.748, 3.408, -0.324, -5.361, 0.246, -2.383, -5.026, 8.448,
           6.331, -5.123, -2.712, -1.342, -0.414, 2.724, 3.833, -6.056, -5.697, 2.902, 4.323, 2.103, 0.915, -4.008,
           -1.234, 3.571, -3.153, -4.524, 4.583, 3.868, -1.537, -0.844, 1.427, 2.996, -5.717, -5.674, 7.207, 4.816,
           -0.98, 4.471, 0.299, -2.479, -6.938, -6.056, 1.035, 3.185, 2.012, 1.138, -1.669, 3.622, -1.251, -0.536, 3.67,
           -9.571, 3.405, 7.92, -3.964, -0.661, 2.031, 0.52, 14.195, 3.802, -21.305, -8.313, -0.532, -3.481, 0.0, 0.0,
           0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 19.902, 109.569, 188.203, 201.817, 209.417,
           210.696, 187.073, 125.547, 59.906, 13.356, -13.057, -27.851, -43.266, -46.625, -41.973, -26.668, -2.586,
           8.665, 16.666, 20.58, 9.953, 4.472, -5.757, -14.732, -20.15, -21.678, -6.767, 2.414, 1.774, -4.517, 8.987,
           20.601, 0.867, -0.161, 0.823, -16.605, -2.269, 5.916, -2.149, 0.757, 3.689, 4.946, 2.432]
    mtf = [1141.594, 1136.4924428613838, 1179.979352441388, 1266.9373022925492, 1269.1512490975674, 1206.0892867861755,
           1165.4815695865339, 1151.3676578296447, 1123.503822245613, 1101.931029737585, 1023.136453018728,
           719.4303261024895, 419.196561473857, 303.2702212488808, 334.1971549533646, 255.9167430126146,
           252.1408943418832, 184.01891470832695, 91.0687639338029, 118.9864985497962, 86.89114120992375,
           94.77483845707731, 132.3085602422052, 91.5343978780574, 100.66368648716988, 117.62920780023744,
           154.18205644015796, 154.39484776702884, 155.67478027041167, 105.96270597342654, 124.07229161672967,
           90.37454926389259, 84.78681277179842, 147.03291212064235, 35.146081313863405, 83.46071214744545,
           113.10630249528431, 46.42621876754548, 47.03825037645255, 48.50368248667547, 145.53402145319086,
           36.95855833657911, 73.45043549400162, 77.11895999279793, 56.21923464501214, 93.53050178488499,
           31.989087248904745, 96.56689803081329, 14.454553900943878, 39.44818695681396, 15.11006169862066,
           48.22936726434023, 42.00159812444878, 31.610996990560157, 17.88561904509028, 19.349782814410478,
           7.0351163439708015, 12.108715431778306, 19.925230064092695, 18.027988833913653, 5.670306194789955,
           7.482701219712112, 9.0815252442289, 1.9862265244667747, 1.1620000000001482, 1.9862265244667474,
           9.081525244228798, 7.482701219712181, 5.670306194789841, 18.027988833913625, 19.92523006409281,
           12.108715431778288, 7.0351163439708015, 19.349782814410446, 17.88561904509034, 31.61099699056014,
           42.00159812444882, 48.22936726434018, 15.11006169862059, 39.44818695681402, 14.454553900943878,
           96.56689803081335, 31.989087248904735, 93.53050178488493, 56.21923464501217, 77.11895999279797,
           73.45043549400162, 36.95855833657904, 145.53402145319086, 48.50368248667542, 47.03825037645251,
           46.42621876754542, 113.1063024952843, 83.46071214744549, 35.146081313863526, 147.03291212064244,
           84.78681277179842, 90.37454926389255, 124.07229161672964, 105.96270597342658, 155.6747802704117,
           154.3948477670289, 154.182056440158, 117.6292078002374, 100.66368648716988, 91.53439787805746,
           132.30856024220526, 94.7748384570773, 86.89114120992375, 118.98649854979622, 91.06876393380291,
           184.018914708327, 252.1408943418832, 255.91674301261452, 334.1971549533646, 303.2702212488808,
           419.1965614738571, 719.4303261024895, 1023.1364530187282, 1101.9310297375853, 1123.503822245613,
           1151.3676578296447, 1165.4815695865339, 1206.0892867861755, 1269.1512490975672, 1266.937302292549,
           1179.979352441388, 1136.4924428613838]
    VOID_MEAN = 12.3975
    SIGNAL_MEAN = 1643.535
    EDGE_MEAN = 511.6325
    TOP_EDGE_MEAN = 625.395
    MTF_FE = 0.4861299156047701
    MTF_PE = 0.47997735363756855
    bisecting_normal = (273, 257, 313, 263)

    def setUp(self) -> None:
        self.hazen_spatial_resolution = SpatialResolution(input_data=self.files,
                                                          report_dir=pathlib.PurePath.joinpath(TEST_REPORT_DIR))

    def test_get_roi(self):
        pixels = np.zeros((256, 256))
        centre = (128, 128)
        size = 20
        roi = self.hazen_spatial_resolution.get_roi(pixels, centre, size)
        assert roi.shape == (20, 20)
        assert roi.mean() == 0
        assert roi.max() == 0
        pixels = np.ones((256, 256))
        roi = self.hazen_spatial_resolution.get_roi(pixels, centre, size)
        assert roi.shape == (20, 20)
        assert roi.mean() == 1.0
        assert roi.max() == 1.0

    def test_get_circles(self):
        img = rescale_to_byte(self.hazen_spatial_resolution.dcm_list[0].pixel_array)
        circles = self.hazen_spatial_resolution.get_circles(img)
        assert np.testing.assert_allclose(circles[0][0][:], self.CIRCLE[0][0][:]) is None

    def test_thresh_image(self):
        img = rescale_to_byte(self.hazen_spatial_resolution.dcm_list[0].pixel_array)
        thresh = self.hazen_spatial_resolution.thresh_image(img)
        assert np.count_nonzero(thresh) < np.count_nonzero(img)

    def test_find_square(self):
        img = rescale_to_byte(self.hazen_spatial_resolution.dcm_list[0].pixel_array)
        thresh = self.hazen_spatial_resolution.thresh_image(img)
        square, _ = self.hazen_spatial_resolution.find_square(thresh)

        assert np.testing.assert_allclose(square, self.TEST_SQUARE) is None

    def test_get_bisecting_normals(self):
        img = rescale_to_byte(self.hazen_spatial_resolution.dcm_list[0].pixel_array)
        thresh = self.hazen_spatial_resolution.thresh_image(img)
        square, _ = self.hazen_spatial_resolution.find_square(thresh)
        vector = {"x": square[3][0] - square[0][0], "y": square[3][1] - square[0][1]}
        centre = {"x": square[0][0] + int(vector["x"] / 2), "y": square[0][1] + int(vector["y"] / 2)}
        n1x, n1y, n2x, n2y = self.hazen_spatial_resolution.get_bisecting_normal(vector, centre)
        assert (n1x, n1y, n2x, n2y) == self.bisecting_normal

    def test_get_top_edge_vector_and_centre(self):
        vector, centre = self.hazen_spatial_resolution.get_top_edge_vector_and_centre(self.TEST_SQUARE)
        assert centre == self.TOP_CENTRE

    def test_get_right_edge_vector_and_centre(self):
        vector, centre = self.hazen_spatial_resolution.get_right_edge_vector_and_centre(self.TEST_SQUARE)
        assert centre == self.CENTRE

    def test_get_void_roi(self):
        pixels = self.hazen_spatial_resolution.dcm_list[0].pixel_array
        void_arr = self.hazen_spatial_resolution.get_void_roi(pixels, self.CIRCLE)

        assert np.mean(void_arr) == self.VOID_MEAN

    def test_get_edge_roi(self):
        pixels = self.hazen_spatial_resolution.dcm_list[0].pixel_array
        edge_arr = self.hazen_spatial_resolution.get_edge_roi(pixels, self.CENTRE)
        assert np.mean(edge_arr) == self.EDGE_MEAN
        edge_arr = self.hazen_spatial_resolution.get_edge_roi(pixels, self.TOP_CENTRE)
        assert np.mean(edge_arr) == self.TOP_EDGE_MEAN

    def test_get_signal_roi(self):
        pixels = self.hazen_spatial_resolution.dcm_list[0].pixel_array
        signal_roi = self.hazen_spatial_resolution.get_signal_roi(pixels, 'right', self.CENTRE, self.CIRCLE)
        assert np.mean(signal_roi) == self.SIGNAL_MEAN

    def test_edge_is_vertical(self):
        mean = np.mean([self.void_roi, self.signal_roi])
        assert self.hazen_spatial_resolution.edge_is_vertical(np.asarray(self.edge_roi).reshape(20, 20), mean) is True

    def test_get_edge(self):
        mean_value = np.mean([self.signal_roi, self.void_roi])
        assert self.x_edge, self.y_edge == self.hazen_spatial_resolution.get_edge(
            self.edge_roi, mean_value, self.hazen_spatial_resolution.dcm_list[0].PixelSpacing)

        assert self.x_edge, self.y_edge == self.hazen_spatial_resolution.get_edge(
            self.rotated_edge_roi, mean_value, self.hazen_spatial_resolution.dcm_list[0].PixelSpacing)

    def test_get_edge_angle_intercept(self):
        assert self.angle, self.intercept == self.hazen_spatial_resolution.get_edge_angle_and_intercept(
            self.x_edge, self.y_edge)

    def test_get_edge_profile_coords(self):
        a, b = self.hazen_spatial_resolution.get_edge_profile_coords(self.angle, self.intercept,
                                                                     self.hazen_spatial_resolution.dcm_list[0].PixelSpacing)
        assert self.x, self.y == (a.flatten(), b.flatten())

    def test_get_esf(self):
        assert self.u, self.esf == self.hazen_spatial_resolution.get_esf(self.rotated_edge_roi, self.y)

    def test_deri(self):
        a = [round(num, 3) for num in self.lsf]
        b = [round(num, 3) for num in self.hazen_spatial_resolution.deri(self.esf)]
        assert a == b

    def test_mtf(self):
        assert self.mtf[0] == abs(np.fft.fft(self.lsf))[0]

    def test_calculate_mtf(self):
        res = self.hazen_spatial_resolution.calculate_mtf(self.hazen_spatial_resolution.dcm_list[0])
        fe_res = res['frequency_encoding_direction']
        pe_res = res['phase_encoding_direction']

        print("\ntest_calculate_mtf.py::TestCalculateMtf::test_calculate_mtf")
        print("new_release_value:", fe_res)
        print("fixed_value:", self.MTF_FE)


        assert fe_res == pytest.approx(self.MTF_FE)
        assert pe_res == pytest.approx(self.MTF_PE)

class TestPhilipsResolution(TestSpatialResolution):
    RESOLUTION_DATA = pathlib.Path(TEST_DATA_DIR / 'resolution')
    # dicom = pydicom.read_file(str(RESOLUTION_DATA / 'philips' / "IM-0004-0002.dcm"))
    files = get_dicom_files(os.path.join(TEST_DATA_DIR, 'resolution', 'philips'))
    TEST_SQUARE = [[293, 203], [215, 218], [230, 297], [308, 282]]
    CIRCLE = [[[257, 245, 199]]]
    TOP_CENTRE = {'x': 254, 'y': 210}
    CENTRE = {'x': 300, 'y': 242}
    VOID_MEAN = 12.29
    EDGE_MEAN = 133.57
    TOP_EDGE_MEAN = 205.28
    SIGNAL_MEAN = 348.5525
    MTF_FE = 0.6017507296855603
    MTF_PE = 0.4923415061063675
    bisecting_normal = (281, 245, 319, 239)


class TestSite01Resolution(TestSpatialResolution):

    files = get_dicom_files(os.path.join(TEST_DATA_DIR, 'resolution', 'resolution_site01'))

    TEST_SQUARE = [[142, 105], [104, 113], [112, 152], [150, 144]]
    CIRCLE = [[[127, 128, 96]]]
    TOP_CENTRE = {'x': 123, 'y': 109}
    CENTRE = {'x': 146, 'y': 124}
    VOID_MEAN = 10.6375
    EDGE_MEAN = 530.86
    TOP_EDGE_MEAN = 648.46

    SIGNAL_MEAN = 1576.69
    MTF_FE = 0.9924200730536655
    MTF_PE = 0.9924200730536658
    bisecting_normal = (137, 126, 155, 122)
