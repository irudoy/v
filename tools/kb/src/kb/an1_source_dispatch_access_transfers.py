"""Natural dispatcher/callee controls and independent full-RAM and source-cell bindings."""
from kb import test_contract
from kb import an1_source_dispatch_access_contract as contract

# Exact per-site physical operand carriers from the complete frozen assembly boundary.
OPERANDS={138172: ('write', 4, 2, 'pre', 15, 0, 0),
 138178: ('write', 4, 3, 'pre', 15, 0, 0),
 138242: ('read', 4, 3, 'base', 15, 0, 0),
 138246: ('read', 4, 2, 'base', 15, 0, 0),
 138248: ('write', 4, 4, 'pre', 15, 0, 0),
 138344: ('read', 4, 4, 'base', 15, 0, 0),
 138346: ('read', 4, 3, 'base', 15, 0, 0),
 138350: ('read', 4, 2, 'base', 15, 0, 0),
 138352: ('read', 4, 1, 'fixed', 138456, 0, 0),
 138354: ('read', 4, 2, 'fixed', 138460, 0, 0),
 138356: ('write', 4, 2, 'base', 1, 0, 0),
 138362: ('read', 4, 2, 'base', 15, 0, 0),
 138448: ('read', 4, 3, 'base', 15, 0, 0),
 138452: ('read', 4, 2, 'base', 15, 0, 0),
 156576: ('read', 2, 0, 'fixed', 156596, 0, 0),
 156584: ('read', 4, 6, 'fixed', 156600, 0, 0),
 156594: ('read', 1, 0, 'base', 4, 0, 0),
 157508: ('write', 4, 0, 'pre', 15, 0, 0),
 157522: ('read', 4, 2, 'base', 15, 0, 0),
 158368: ('read', 2, 1, 'base', 4, 0, 0),
 158370: ('read', 2, 0, 'offset', 4, 2, 0),
 158380: ('read', 1, 1, 'base', 4, 0, 0),
 158382: ('read', 1, 0, 'offset', 4, 1, 0),
 158388: ('read', 4, 6, 'fixed', 158396, 0, 0),
 250456: ('write', 4, 12, 'pre', 15, 0, 0),
 250458: ('write', 4, 13, 'pre', 15, 0, 0),
 250460: ('write', 4, 14, 'pre', 15, 0, 0),
 250462: ('read', 4, 1, 'fixed', 251128, 0, 0),
 250466: ('read', 2, 0, 'fixed', 250830, 0, 0),
 250474: ('read', 1, 12, 'indexed', 1, 0, 0),
 250484: ('read', 2, 0, 'fixed', 250832, 0, 0),
 250490: ('read', 4, 2, 'fixed', 251132, 0, 0),
 250492: ('read', 1, 6, 'indexed', 1, 0, 0),
 250500: ('read', 2, 6, 'indexed', 2, 0, 0),
 250508: ('read', 2, 0, 'fixed', 250832, 0, 0),
 250512: ('read', 4, 14, 'fixed', 251136, 0, 0),
 250514: ('read', 1, 2, 'indexed', 1, 0, 0),
 250520: ('write', 1, 2, 'indexed', 1, 0, 0),
 250522: ('read', 4, 14, 'fixed', 251136, 0, 0),
 250532: ('read', 2, 5, 'indexed', 2, 0, 0),
 250566: ('write', 2, 4, 'indexed', 14, 0, 0),
 250576: ('read', 2, 0, 'fixed', 250830, 0, 0),
 250578: ('write', 1, 12, 'indexed', 1, 0, 0),
 250580: ('read', 4, 14, 'base', 15, 0, 0),
 250582: ('read', 4, 13, 'base', 15, 0, 0),
 250586: ('read', 4, 12, 'base', 15, 0, 0),
 250588: ('write', 4, 12, 'pre', 15, 0, 0),
 250590: ('write', 4, 13, 'pre', 15, 0, 0),
 250592: ('write', 4, 14, 'pre', 15, 0, 0),
 250594: ('write', 4, 'pr', 'pre', 15, 0, 0),
 250596: ('write', 4, 'gbr', 'pre', 15, 0, 0),
 250598: ('read', 4, 0, 'fixed', 251140, 0, 0),
 250604: ('tst', 1, None, 'indexed', 'gbr', 0, 1),
 250610: ('tst', 1, None, 'indexed', 'gbr', 0, 16),
 250614: ('tst', 1, None, 'indexed', 'gbr', 0, 2),
 250620: ('tst', 1, None, 'indexed', 'gbr', 0, 32),
 250624: ('read', 4, 2, 'fixed', 251136, 0, 0),
 250638: ('write', 1, 1, 'indexed', 2, 0, 0),
 250640: ('read', 4, 14, 'fixed', 251136, 0, 0),
 250656: ('read', 4, 4, 'fixed', 251144, 0, 0),
 250658: ('read', 2, 2, 'indexed', 5, 0, 0),
 250666: ('read', 4, 2, 'fixed', 251148, 0, 0),
 250678: ('write', 1, 2, 'indexed', 14, 0, 0),
 250680: ('read', 4, 'gbr', 'base', 15, 0, 0),
 250682: ('read', 4, 'pr', 'base', 15, 0, 0),
 250684: ('read', 4, 14, 'base', 15, 0, 0),
 250686: ('read', 4, 13, 'base', 15, 0, 0),
 250690: ('read', 4, 12, 'base', 15, 0, 0),
 250692: ('write', 4, 14, 'pre', 15, 0, 0),
 250694: ('write', 4, 'pr', 'pre', 15, 0, 0),
 250696: ('write', 4, 'gbr', 'pre', 15, 0, 0),
 250698: ('read', 4, 0, 'fixed', 251152, 0, 0),
 250702: ('read', 4, 2, 'fixed', 251136, 0, 0),
 250714: ('read', 1, 6, 'indexed', 2, 0, 0),
 250732: ('write', 1, 3, 'indexed', 2, 0, 0),
 250748: ('read', 4, 2, 'fixed', 251156, 0, 0),
 250780: ('write', 1, 6, 'indexed', 2, 0, 0),
 250788: ('write', 1, 3, 'indexed', 2, 0, 0),
 250790: ('read', 4, 'gbr', 'base', 15, 0, 0),
 250792: ('read', 4, 'pr', 'base', 15, 0, 0),
 250796: ('read', 4, 14, 'base', 15, 0, 0),
 250798: ('read', 4, 5, 'fixed', 251136, 0, 0),
 250804: ('read', 4, 2, 'fixed', 251128, 0, 0),
 250812: ('read', 2, 1, 'fixed', 250834, 0, 0),
 250816: ('read', 2, 6, 'indexed', 5, 0, 0),
 250828: ('write', 1, 6, 'indexed', 2, 0, 0),
 250836: ('read', 4, 5, 'fixed', 251160, 0, 0),
 250838: ('read', 1, 0, 'base', 5, 0, 0),
 250846: ('read', 4, 5, 'fixed', 251152, 0, 0),
 250850: ('read', 1, 2, 'indexed', 5, 0, 0),
 250858: ('read', 4, 7, 'fixed', 251164, 0, 0),
 250862: ('read', 2, 0, 'fixed', 251118, 0, 0),
 250866: ('read', 1, 2, 'indexed', 7, 0, 0),
 250872: ('write', 1, 2, 'indexed', 7, 0, 0),
 250874: ('read', 4, 7, 'fixed', 251164, 0, 0),
 250878: ('read', 2, 0, 'fixed', 251118, 0, 0),
 250884: ('read', 1, 4, 'indexed', 7, 0, 0),
 250894: ('read', 2, 0, 'fixed', 251118, 0, 0),
 250898: ('write', 1, 4, 'indexed', 7, 0, 0),
 250908: ('write', 4, 14, 'pre', 15, 0, 0),
 250910: ('write', 4, 'pr', 'pre', 15, 0, 0),
 250912: ('read', 4, 5, 'fixed', 251164, 0, 0),
 250924: ('read', 1, 6, 'indexed', 2, 0, 0),
 250940: ('read', 4, 2, 'fixed', 251136, 0, 0),
 250950: ('read', 1, 6, 'indexed', 2, 0, 0),
 250952: ('read', 4, 2, 'fixed', 251168, 0, 0),
 250958: ('write', 1, 6, 'indexed', 2, 0, 0),
 250964: ('write', 1, 6, 'indexed', 5, 0, 0),
 250966: ('read', 4, 'pr', 'base', 15, 0, 0),
 250970: ('read', 4, 14, 'base', 15, 0, 0),
 250974: ('read', 4, 6, 'fixed', 251172, 0, 0),
 250976: ('read', 1, 0, 'offset', 6, 6, 0),
 250984: ('read', 1, 0, 'base', 6, 0, 0),
 250990: ('read', 4, 2, 'fixed', 251128, 0, 0),
 250992: ('read', 2, 0, 'fixed', 251120, 0, 0),
 250994: ('read', 1, 6, 'indexed', 2, 0, 0),
 251006: ('read', 4, 2, 'fixed', 251136, 0, 0),
 251012: ('read', 4, 7, 'fixed', 251128, 0, 0),
 251016: ('read', 2, 6, 'fixed', 251122, 0, 0),
 251020: ('read', 1, 5, 'indexed', 2, 0, 0),
 251026: ('read', 1, 6, 'indexed', 2, 0, 0),
 251036: ('write', 4, 5, 'base', 15, 0, 0),
 251038: ('read', 2, 2, 'fixed', 251122, 0, 0),
 251042: ('write', 1, 5, 'indexed', 7, 0, 0),
 251048: ('write', 4, 14, 'pre', 15, 0, 0),
 251050: ('write', 4, 'pr', 'pre', 15, 0, 0),
 251052: ('read', 4, 5, 'fixed', 251132, 0, 0),
 251062: ('read', 4, 4, 'fixed', 251144, 0, 0),
 251064: ('read', 2, 6, 'indexed', 5, 0, 0),
 251066: ('read', 4, 2, 'fixed', 251148, 0, 0),
 251084: ('read', 4, 2, 'fixed', 251128, 0, 0),
 251090: ('read', 2, 3, 'fixed', 251124, 0, 0),
 251098: ('write', 1, 6, 'indexed', 2, 0, 0),
 251100: ('read', 4, 2, 'fixed', 251128, 0, 0),
 251104: ('read', 2, 3, 'fixed', 251124, 0, 0),
 251110: ('write', 1, 1, 'indexed', 2, 0, 0),
 251112: ('read', 4, 'pr', 'base', 15, 0, 0),
 251116: ('read', 4, 14, 'base', 15, 0, 0),
 251176: ('read', 4, 5, 'fixed', 251760, 0, 0),
 251178: ('read', 1, 0, 'offset', 5, 9, 0),
 251186: ('read', 4, 4, 'fixed', 251764, 0, 0),
 251192: ('read', 4, 1, 'fixed', 251768, 0, 0),
 251194: ('read', 1, 2, 'indexed', 4, 0, 0),
 251196: ('read', 2, 0, 'fixed', 251474, 0, 0),
 251198: ('write', 1, 2, 'indexed', 1, 0, 0),
 251200: ('read', 2, 0, 'fixed', 251476, 0, 0),
 251202: ('write', 1, 2, 'indexed', 1, 0, 0),
 251204: ('read', 2, 0, 'fixed', 251478, 0, 0),
 251206: ('write', 1, 2, 'indexed', 1, 0, 0),
 251208: ('read', 2, 0, 'fixed', 251480, 0, 0),
 251210: ('write', 1, 2, 'indexed', 1, 0, 0),
 251212: ('read', 2, 0, 'fixed', 251482, 0, 0),
 251214: ('write', 1, 2, 'indexed', 1, 0, 0),
 251216: ('read', 2, 0, 'fixed', 251484, 0, 0),
 251218: ('write', 1, 2, 'indexed', 1, 0, 0),
 251220: ('read', 2, 0, 'fixed', 251486, 0, 0),
 251222: ('write', 1, 2, 'indexed', 1, 0, 0),
 251230: ('write', 1, 0, 'offset', 5, 9, 0),
 251232: ('read', 2, 6, 'fixed', 251488, 0, 0),
 251234: ('read', 1, 0, 'base', 6, 0, 0),
 251240: ('read', 4, 1, 'fixed', 251768, 0, 0),
 251242: ('read', 2, 0, 'fixed', 251484, 0, 0),
 251244: ('read', 4, 4, 'fixed', 251764, 0, 0),
 251246: ('read', 1, 7, 'indexed', 1, 0, 0),
 251248: ('read', 2, 0, 'fixed', 251486, 0, 0),
 251250: ('write', 1, 7, 'indexed', 1, 0, 0),
 251254: ('read', 2, 0, 'fixed', 251482, 0, 0),
 251256: ('read', 1, 2, 'indexed', 1, 0, 0),
 251258: ('read', 2, 0, 'fixed', 251484, 0, 0),
 251260: ('write', 1, 2, 'indexed', 1, 0, 0),
 251262: ('read', 2, 0, 'fixed', 251480, 0, 0),
 251264: ('read', 1, 2, 'indexed', 1, 0, 0),
 251266: ('read', 2, 0, 'fixed', 251482, 0, 0),
 251268: ('write', 1, 2, 'indexed', 1, 0, 0),
 251270: ('read', 2, 0, 'fixed', 251478, 0, 0),
 251272: ('read', 1, 2, 'indexed', 1, 0, 0),
 251274: ('read', 2, 0, 'fixed', 251480, 0, 0),
 251276: ('write', 1, 2, 'indexed', 1, 0, 0),
 251278: ('read', 2, 0, 'fixed', 251476, 0, 0),
 251280: ('read', 1, 2, 'indexed', 1, 0, 0),
 251282: ('read', 2, 0, 'fixed', 251478, 0, 0),
 251284: ('write', 1, 2, 'indexed', 1, 0, 0),
 251286: ('read', 2, 0, 'fixed', 251474, 0, 0),
 251288: ('read', 1, 2, 'indexed', 1, 0, 0),
 251290: ('read', 2, 0, 'fixed', 251476, 0, 0),
 251292: ('write', 1, 2, 'indexed', 1, 0, 0),
 251298: ('read', 1, 2, 'indexed', 4, 0, 0),
 251300: ('read', 2, 0, 'fixed', 251474, 0, 0),
 251302: ('write', 1, 2, 'indexed', 1, 0, 0),
 251314: ('read', 2, 0, 'fixed', 251490, 0, 0),
 251320: ('write', 1, 2, 'indexed', 1, 0, 0),
 251322: ('read', 2, 0, 'fixed', 251490, 0, 0),
 251326: ('write', 1, 2, 'indexed', 1, 0, 0),
 251332: ('write', 4, 'gbr', 'pre', 15, 0, 0),
 251334: ('read', 4, 0, 'fixed', 251760, 0, 0),
 251338: ('read', 4, 2, 'fixed', 251772, 0, 0),
 251342: ('read', 1, 1, 'indexed', 2, 0, 0),
 251344: ('read', 4, 2, 'fixed', 251776, 0, 0),
 251346: ('read', 1, 0, 'offset', 'gbr', 29, 0),
 251348: ('read', 1, 4, 'base', 2, 0, 0),
 251356: ('read', 1, 0, 'offset', 'gbr', 169, 0),
 251370: ('write', 1, 0, 'offset', 'gbr', 29, 0),
 251374: ('read', 4, 6, 'fixed', 251780, 0, 0),
 251378: ('write', 1, 0, 'offset', 'gbr', 29, 0),
 251380: ('read', 1, 0, 'base', 6, 0, 0),
 251382: ('write', 1, 0, 'offset', 'gbr', 169, 0),
 251386: ('read', 4, 'gbr', 'base', 15, 0, 0),
 251388: ('write', 4, 'gbr', 'pre', 15, 0, 0),
 251390: ('read', 4, 0, 'fixed', 251784, 0, 0),
 251394: ('read', 1, 0, 'offset', 'gbr', 178, 0),
 251398: ('read', 1, 0, 'offset', 'gbr', 0, 0),
 251404: ('read', 1, 0, 'offset', 'gbr', 2, 0),
 251428: ('write', 1, 0, 'offset', 'gbr', 178, 0),
 251430: ('read', 1, 0, 'offset', 'gbr', 178, 0),
 251436: ('read', 4, 6, 'fixed', 251788, 0, 0),
 251440: ('read', 1, 2, 'indexed', 6, 0, 0),
 251452: ('or', 1, None, 'indexed', 'gbr', 0, 32),
 251454: ('read', 4, 6, 'fixed', 251792, 0, 0),
 251460: ('read', 1, 2, 'base', 6, 0, 0),
 251462: ('read', 4, 6, 'fixed', 251788, 0, 0),
 251464: ('and', 1, None, 'indexed', 'gbr', 0, 223),
 251468: ('write', 1, 2, 'indexed', 6, 0, 0),
 251472: ('read', 4, 'gbr', 'base', 15, 0, 0),
 251492: ('read', 4, 4, 'fixed', 251796, 0, 0),
 251494: ('read', 4, 2, 'fixed', 251800, 0, 0),
 251496: ('read', 1, 0, 'offset', 4, 1, 0),
 251500: ('read', 1, 0, 'offset', 2, 7, 0),
 251508: ('read', 1, 2, 'base', 4, 0, 0),
 251516: ('read', 4, 5, 'fixed', 251760, 0, 0),
 251520: ('read', 1, 0, 'indexed', 5, 0, 0),
 251526: ('read', 4, 7, 'fixed', 251768, 0, 0),
 251528: ('read', 2, 0, 'fixed', 251752, 0, 0),
 251530: ('read', 4, 4, 'fixed', 251804, 0, 0),
 251532: ('read', 1, 6, 'indexed', 7, 0, 0),
 251534: ('read', 1, 2, 'base', 4, 0, 0),
 251542: ('read', 1, 0, 'indexed', 5, 0, 0),
 251548: ('read', 2, 6, 'fixed', 251754, 0, 0),
 251550: ('read', 1, 0, 'base', 6, 0, 0),
 251556: ('read', 2, 0, 'fixed', 251756, 0, 0),
 251562: ('read', 1, 6, 'indexed', 7, 0, 0),
 251576: ('read', 2, 0, 'fixed', 251756, 0, 0),
 251580: ('write', 1, 2, 'indexed', 7, 0, 0),
 251586: ('write', 4, 'gbr', 'pre', 15, 0, 0),
 251588: ('read', 4, 0, 'fixed', 251760, 0, 0),
 251592: ('read', 1, 0, 'offset', 'gbr', 17, 0),
 251600: ('read', 4, 2, 'fixed', 251772, 0, 0),
 251604: ('read', 4, 4, 'fixed', 251776, 0, 0),
 251606: ('read', 1, 6, 'indexed', 2, 0, 0),
 251608: ('read', 1, 2, 'base', 4, 0, 0),
 251618: ('write', 1, 0, 'offset', 'gbr', 17, 0),
 251624: ('or', 1, None, 'indexed', 'gbr', 0, 8),
 251626: ('read', 4, 2, 'fixed', 251768, 0, 0),
 251628: ('read', 2, 0, 'fixed', 251756, 0, 0),
 251630: ('read', 4, 4, 'fixed', 251808, 0, 0),
 251632: ('read', 1, 6, 'indexed', 2, 0, 0),
 251634: ('read', 1, 2, 'base', 4, 0, 0),
 251644: ('write', 1, 0, 'offset', 'gbr', 17, 0),
 251648: ('read', 4, 'gbr', 'base', 15, 0, 0),
 251650: ('write', 4, 'gbr', 'pre', 15, 0, 0),
 251652: ('read', 4, 0, 'fixed', 251764, 0, 0),
 251656: ('read', 4, 2, 'fixed', 251812, 0, 0),
 251660: ('read', 1, 4, 'indexed', 2, 0, 0),
 251662: ('read', 4, 2, 'fixed', 251800, 0, 0),
 251666: ('read', 1, 0, 'offset', 2, 4, 0),
 251684: ('read', 4, 4, 'fixed', 251816, 0, 0),
 251686: ('read', 1, 2, 'base', 4, 0, 0),
 251694: ('read', 4, 6, 'fixed', 251820, 0, 0),
 251698: ('read', 1, 2, 'base', 6, 0, 0),
 251706: ('read', 4, 2, 'fixed', 251824, 0, 0),
 251708: ('read', 1, 0, 'offset', 'gbr', 190, 0),
 251710: ('read', 1, 4, 'base', 2, 0, 0),
 251724: ('read', 1, 0, 'offset', 'gbr', 190, 0),
 251726: ('read', 4, 2, 'fixed', 251824, 0, 0),
 251730: ('read', 1, 0, 'offset', 2, 1, 0),
 251746: ('write', 1, 0, 'offset', 'gbr', 188, 0),
 251750: ('read', 4, 'gbr', 'base', 15, 0, 0),
 251828: ('read', 4, 5, 'fixed', 252128, 0, 0),
 251832: ('read', 1, 6, 'indexed', 5, 0, 0),
 251840: ('read', 4, 4, 'fixed', 252132, 0, 0),
 251846: ('read', 1, 2, 'indexed', 4, 0, 0),
 251852: ('write', 1, 2, 'indexed', 4, 0, 0),
 251860: ('write', 1, 6, 'indexed', 5, 0, 0),
 251866: ('read', 4, 1, 'fixed', 252128, 0, 0),
 251870: ('read', 1, 5, 'indexed', 1, 0, 0),
 251878: ('read', 4, 2, 'fixed', 252136, 0, 0),
 251882: ('read', 4, 6, 'fixed', 252132, 0, 0),
 251884: ('read', 1, 7, 'indexed', 2, 0, 0),
 251888: ('read', 4, 2, 'fixed', 252140, 0, 0),
 251892: ('read', 1, 4, 'indexed', 2, 0, 0),
 251906: ('write', 1, 4, 'indexed', 6, 0, 0),
 251908: ('write', 1, 7, 'indexed', 6, 0, 0),
 251918: ('write', 1, 5, 'indexed', 1, 0, 0),
 251924: ('read', 4, 6, 'fixed', 252128, 0, 0),
 251928: ('read', 1, 0, 'indexed', 6, 0, 0),
 251934: ('read', 4, 6, 'fixed', 252132, 0, 0),
 251940: ('read', 1, 2, 'indexed', 6, 0, 0),
 251944: ('read', 4, 6, 'fixed', 252140, 0, 0),
 251948: ('write', 1, 2, 'indexed', 6, 0, 0),
 251954: ('write', 4, 12, 'pre', 15, 0, 0),
 251956: ('write', 4, 13, 'pre', 15, 0, 0),
 251958: ('write', 4, 14, 'pre', 15, 0, 0),
 251960: ('write', 4, 'pr', 'pre', 15, 0, 0),
 251962: ('write', 4, 'gbr', 'pre', 15, 0, 0),
 251964: ('read', 4, 0, 'fixed', 252132, 0, 0),
 251970: ('read', 4, 14, 'fixed', 252144, 0, 0),
 251982: ('read', 2, 0, 'offset', 'gbr', 180, 0),
 251988: ('write', 2, 0, 'offset', 'gbr', 178, 0),
 251994: ('read', 1, 0, 'offset', 'gbr', 186, 0),
 252000: ('write', 1, 0, 'offset', 'gbr', 185, 0),
 252006: ('read', 4, 6, 'fixed', 252148, 0, 0),
 252012: ('read', 1, 2, 'indexed', 6, 0, 0),
 252018: ('write', 1, 2, 'indexed', 6, 0, 0),
 252024: ('read', 2, 0, 'fixed', 252120, 0, 0),
 252028: ('read', 1, 0, 'indexed', 14, 0, 0),
 252032: ('write', 1, 0, 'offset', 'gbr', 184, 0),
 252038: ('read', 4, 6, 'fixed', 252140, 0, 0),
 252044: ('read', 1, 2, 'indexed', 6, 0, 0),
 252048: ('read', 4, 6, 'fixed', 252136, 0, 0),
 252052: ('write', 1, 2, 'indexed', 6, 0, 0),
 252058: ('read', 2, 0, 'fixed', 252122, 0, 0),
 252060: ('read', 1, 0, 'indexed', 14, 0, 0),
 252064: ('write', 1, 0, 'offset', 'gbr', 190, 0),
 252094: ('read', 2, 0, 'fixed', 252124, 0, 0),
 252096: ('read', 1, 2, 'indexed', 14, 0, 0),
 252098: ('read', 2, 0, 'fixed', 252126, 0, 0),
 252102: ('write', 1, 2, 'indexed', 14, 0, 0),
 252108: ('read', 4, 'gbr', 'base', 15, 0, 0),
 252110: ('read', 4, 'pr', 'base', 15, 0, 0),
 252112: ('read', 4, 14, 'base', 15, 0, 0),
 252114: ('read', 4, 13, 'base', 15, 0, 0),
 252118: ('read', 4, 12, 'base', 15, 0, 0)}

ROOT_CALLS=((0x3D846,0x3D258,0),(0x3D84A,0x3D258,1),(0x3D852,0x3D2DC,0),(0x3D856,0x3D2DC,1),
    (0x3D85E,0x3D344,0),(0x3D862,0x3D344,1),(0x3D870,0x3D3AE,0),(0x3D874,0x3D3AE,1),
    (0x3D87E,0x3D41C,0),(0x3D882,0x3D41C,1),(0x3D892,0x3D45C,0),(0x3D896,0x3D45C,1),
    (0x3D89E,0x3D528,None),(0x3D8A2,0x3D5C4,None),(0x3D8A6,0x3D5FC,None),(0x3D8AA,0x3D664,None),
    (0x3D8AE,0x3D6C2,None),(0x3D8B2,0x3D7B4,None),(0x3D8B6,0x3D4A8,0),(0x3D8BA,0x3D4A8,1),
    (0x3D8C4,0x3D7DA,None),(0x3D8C8,0x3D814,None))
# The natural dispatcher supplies positive150 and0..38160 to the signed helper.
# Only its short unsigned-magnitude division and possible zero dividend execute.
DIVISION_INFEASIBLE=set(range(0x21C08,0x21CD6,2))|{0x21BCC,0x21BCE,0x21BFE,0x21C00}
# The32-byte wrapper enters the common interpolation core at26A88 with byte mode.
CORE_INFEASIBLE=set(range(0x26A60,0x26A88,2))|set(range(0x26A9C,0x26AAA,2))
INFEASIBLE_SITES=DIVISION_INFEASIBLE|CORE_INFEASIBLE
FEASIBLE_SITES={site for first,last in contract.SPANS for site in range(first,last,2)}-INFEASIBLE_SITES
FIXED_BRANCHES={0x21BC0:'fallthrough',0x21BCA:'taken',0x21BDC:'fallthrough',
    0x21BE4:'fallthrough',0x21BFC:'taken',0x26A9A:'taken'}


def same(actual,wanted,reason):
    if not test_contract.exact(actual,wanted):raise ValueError(reason)


def require_physical_carriers(observed,result,fixture):
    """Check fixed domain operand declarations against live carriers and original bytes."""
    memory=bytearray(observed['memory_before'][0]);frame=bytearray(observed['frame_before']);all_events=[]
    sp=observed['sp']
    for row in result['trace']:
        rule=OPERANDS.get(row['site']);events=[]
        if rule is not None:
            mode,width,register,form,base,offset,immediate=rule;before=row['before'];after=row['after']
            if form=='fixed':address=base
            else:
                address=before['gbr'] if base=='gbr' else before['registers'][base]
                address=(address+(before['registers'][0] if form=='indexed' else -width if form=='pre' else offset))&0xFFFFFFFF
            if address%width:raise ValueError('the AN1 physical operand loses its natural alignment')
            if 0x01000000<=address<=0x01010000-width:
                data,at,domain=memory,address-0x01000000,'ram'
            elif 0xFFFF8400<=address<=0xFFFF8500-width:
                data,at,domain=memory,address&65535,'native-control'
            elif sp-160<=address<=sp+32-width:data,at,domain=frame,address-sp+160,'frame'
            elif 0<=address<=len(fixture)-width:data,at,domain=fixture,address,'rom'
            else:raise ValueError('the AN1 physical operand leaves complete declared ROM,RAM,native or frame storage')
            def event(direction,raw):
                events.append(dict(site=row['site'],mode=direction,address=address,width_bytes=width,
                    register=register if type(register) is int else None,domain=domain,bytes=raw.hex()))
            incoming=bytes(data[at:at+width])
            if mode in ('read','and','or','tst'):event('read',incoming)
            if mode=='read':
                value=int.from_bytes(incoming,'big')
                if width<4 and value&(1<<(width*8-1)):value|=0xFFFFFFFF^((1<<(width*8))-1)
                actual=after['registers'][register] if type(register) is int else after[register]
                if actual!=value:raise ValueError('the AN1 physical load changes the complete live destination carrier')
            elif mode in ('write','and','or'):
                if domain=='rom':raise ValueError('the AN1 natural closure writes a bound ROM operand')
                if mode=='write':value=before['registers'][register] if type(register) is int else before[register]
                else:
                    value=int.from_bytes(incoming,'big');value=value&immediate if mode=='and' else value|immediate
                raw=(value&((1<<(width*8))-1)).to_bytes(width,'big');data[at:at+width]=raw;event('write',raw)
        same(row['accesses'],events,'the AN1 closure changes a complete declared physical site,address,mode,width,register or byte')
        all_events.extend(events)
    same(result['accesses'],all_events,'the AN1 closure omits or invents an ordered physical operand')
    same((result['ram'],result['frame']),(bytes(memory),bytes(frame)),
        'the AN1 complete physical carrier projection changes final RAM or frame bytes')


def call_span(trace,call,cursor=0):
    start=next((i for i in range(cursor,len(trace)) if trace[i]['site']==call['site']),None)
    if start is None or start+2>=len(trace) or trace[start+2]['site']!=call['target']:
        raise ValueError('the AN1 closure loses a natural call delay slot or exact real target')
    after=start+2
    terminal=next((i for i in range(after,len(trace)-1) if trace[i]['word']==0x000B
        and trace[i+1]['next']==call['return_address']),None)
    if terminal is None:raise ValueError('the AN1 closure lacks an exact natural post-delay callee return')
    return after,terminal+1


def require(observed,result,value,fixture):
    same(observed['exit'],(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers'])),
        'the AN1 original changes complete independently reconstructed exit CPU/SR state')
    same((observed['frame_after'],observed['memory_after']),
        (result['frame'],(result['ram'],)),'the AN1 original changes complete reconstructed frame or ordinary RAM')
    same(observed['memory_after'],(value['ram'],),'the AN1 original disagrees with separate complete two-lane RAM equations')
    same([event for event in result['accesses'] if event['domain']=='ram' and event['mode']=='write'],value['writes'],
        'the AN1 closure changes independent ordered physical stores, widths, registers or actual bytes')
    trace=result.get('trace')
    if type(trace) is not list or not trace:raise ValueError('the AN1 closure omits its complete instruction trace')
    require_physical_carriers(observed,result,fixture)
    first=trace[0]['before']
    same(tuple(first[key] for key in ('registers','gbr','mach','macl','sr','pr')),
        ((*observed['context'][:15],observed['sp']),*observed['context'][15:18],observed['sr_before'],observed['continuation']),
        'the AN1 trace changes complete natural entry state')
    for index,row in enumerate(trace):
        next_site=trace[index+1]['site'] if index+1<len(trace) else observed['continuation']
        if (row['site'] not in FEASIBLE_SITES or row['next']!=next_site
                or row['bytes']!=fixture[row['site']:row['site']+2].hex()
                or row['word']!=int.from_bytes(fixture[row['site']:row['site']+2],'big')):
            raise ValueError('the AN1 closure changes a feasible exact instruction, pool-bound path or natural continuation')
        if index+1<len(trace):same(row['after'],trace[index+1]['before'],'the AN1 closure detaches intermediate complete CPU state')
    same(result['code'],{row['site']:fixture[row['site']:row['site']+2].hex() for row in trace},
        'the AN1 closure changes an exact executed instruction byte')
    delayed={row['site']+2 for row in result['branches'] if row['delay']}
    if {row['site'] for row in trace if row['delay_slot']}!=delayed:
        raise ValueError('the AN1 closure loses a real call, branch, tail jump or return delay slot')
    roots=[call for call in result['calls'] if contract.ENTRY<=call['site']<0x3D8D8]
    same(tuple((r['site'],r['target']) for r in roots),tuple((a,b) for a,b,index in ROOT_CALLS),
        'the AN1 dispatcher changes its complete ordered22 natural calls')
    for actual,(site,target,lane) in zip(roots,ROOT_CALLS):
        if (actual['sp']!=observed['sp']-20 or actual['return_address']!=site+4
                or lane is not None and actual['entry']['registers'][4]!=lane):
            raise ValueError('the AN1 dispatcher changes a natural callee SP,PR or post-delay lane argument')
    allowed={(a,b) for a,b,index in ROOT_CALLS}|{(0x3D32E,0x263A0),(0x3D38E,0x21BBC),
        (0x3D434,0x3D3D4),(0x3D4C0,0x263A0)}
    spans=[]
    for call in result['calls']:
        if (call['site'],call['target']) not in allowed:
            raise ValueError('the AN1 closure adds an undeclared or stubbed real call')
        start,end=call_span(trace,call);entered=trace[start]['before'];returned=trace[end]['after']
        same(tuple(call['entry'][key] for key in ('registers','sp','gbr','mach','macl','sr','pr')),
            (tuple(entered['registers'][:15]),entered['registers'][15],entered['gbr'],entered['mach'],
             entered['macl'],entered['sr'],entered['pr']),'the AN1 call detaches its complete post-delay live CPU entry')
        if returned['registers'][15]!=call['sp'] or returned['pr']!=call['return_address']:
            raise ValueError('the AN1 callee changes its natural post-delay SP or PR')
        spans.append((call,start,end,returned))
    actual_lookups=[row for row in spans if row[0]['target']==0x263A0]
    if len(actual_lookups)!=len(value['lookups']):raise ValueError('the AN1 closure omits or invents a selected-table lookup')
    for (call,start,end,returned),lookup in zip(actual_lookups,value['lookups']):
        regs=call['entry']['registers']
        if (call['site']!=lookup['callsite'] or regs[4]!=0x12DEA or regs[5]!=lookup['coordinate']
                or returned['registers'][0]&255!=lookup['value']):
            raise ValueError('the AN1 selected lookup changes its exact live byte coordinate, table or independently calculated return')
        events=[event for row in trace[start:end+1] for event in row['accesses']
            if event['domain']=='rom' and 0x12DEA<=event['address']<0x12E0A]
        index=lookup['index'];sites=((0x263B2,index,0),) if lookup['endpoint'] else (
            (0x26AAC,index,1),(0x26AAE,index+1,0))
        expected=[dict(site=site,mode='read',address=0x12DEA+i,width_bytes=1,register=register,
            domain='rom',bytes=fixture[0x12DEA+i:0x12DEB+i].hex()) for site,i,register in sites]
        same(events,expected,'the AN1 selected table changes a physical byte, neighbor, width or exact load site')
        root=next((r for r in roots if r['site']==lookup['root_call']),None)
        if root is None:raise ValueError('the AN1 selected lookup loses its actual natural dispatcher caller')
        outer_start,outer_end=call_span(trace,root)
        if not outer_start<=start<end<=outer_end:
            raise ValueError('the AN1 selected table read is detached from its declared complete parent invocation')
    divisions=[row for row in spans if row[0]['target']==0x21BBC]
    expected=[temperature for temperature in value['temperature_codes'] if 10<=temperature<170]
    if len(divisions)!=len(expected):raise ValueError('the AN1 conversion omits or invents a real signed division')
    for (call,start,end,returned),temperature in zip(divisions,expected):
        if (tuple(call['entry']['registers'][:2])!=(150,240*(temperature-10))
                or returned['registers'][0]!=240*(temperature-10)//150):
            raise ValueError('the AN1 conversion replaces its real constant-divisor call with a supplied scalar result')
    if (trace[-1]['next']!=observed['continuation'] or result['sp']!=observed['sp']
            or result['pr']!=observed['continuation'] or result['gbr']!=observed['context'][15]):
        raise ValueError('the AN1 dispatcher changes its natural complete post-delay return')
