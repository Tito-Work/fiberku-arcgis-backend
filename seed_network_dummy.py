from decimal import Decimal
from app.core.database import SessionLocal, engine
from app.models.customer import Customer
from app.models.package import Package, PackageCoverage
from app.models.coverage import Coverage
from app.models.segment import Segment
from app.models.operator import Operator
from app.models.fiber_optic import FiberOptic
from app.models.user import User
from app.models.base import BaseModel
from app.utils.audit import set_audit_fields


def upsert_by_id(db, model, data):
    """Create or update a record by id without changing the table schema."""
    existing = db.query(model).filter(model.id == data["id"]).first()

    if existing:
        for key, value in data.items():
            setattr(existing, key, value)
        record = existing
    else:
        record = model(**data)
        set_audit_fields(record, created_by=None)
        db.add(record)

    return record


def create_segments(db):
    segments_data = [
        {
            'id': '01krnmcs3s3ntrsswm27fv4dtq',
            'code': 'SEG001',
            'name': 'Residential',
            'is_active': True,
        },
        {
            'id': '01krnmcs3sn64a091hqrqdy96p',
            'code': 'SEG002',
            'name': 'SME (Small Medium Enterprise)',
            'is_active': True,
        },
        {
            'id': '01krnmcs3sgz7xgyp3yvgdrzg3',
            'code': 'SEG003',
            'name': 'Enterprise',
            'is_active': True,
        },
    ]

    records = []
    for item in segments_data:
        records.append(upsert_by_id(db, Segment, item))

    db.commit()
    return records


def create_operators(db):
    operators_data = [
        {
            'id': '01krnmcs49c6k2948f4b9dhvny',
            'code': 'ISP001',
            'name': 'IndiHome',
            'is_active': True,
        },
        {
            'id': '01krnmcs49cv8cgch9njt8pkc0',
            'code': 'ISP002',
            'name': 'Biznet',
            'is_active': True,
        },
        {
            'id': '01krnmcs49aa0df7jqrdy1p697',
            'code': 'ISP003',
            'name': 'MyRepublic',
            'is_active': True,
        },
        {
            'id': '01krnmcs4938xg4t6zx2w82vh6',
            'code': 'ISP004',
            'name': 'First Media',
            'is_active': True,
        },
        {
            'id': '01krnmcs499nht3j4xndf3h70q',
            'code': 'ISP005',
            'name': 'CBN',
            'is_active': True,
        },
        {
            'id': '01krnmcs49e5mqqmkpmentck5p',
            'code': 'ISP006',
            'name': 'Oxygen',
            'is_active': True,
        },
        {
            'id': '01krnmcs49ynp6p60smsdvnh5p',
            'code': 'ISP007',
            'name': 'IconNet',
            'is_active': True,
        },
    ]

    records = []
    for item in operators_data:
        records.append(upsert_by_id(db, Operator, item))

    db.commit()
    return records


def create_packages(db):
    packages_data = [
        {
            'id': '01krnmcs4kge63eg4nza0ek2cw',
            'name': 'Basic Fiber',
            'description': 'Basic internet package for home users',
            'price': Decimal("250000.00"),
            'color': '#2563eb',
            'is_active': True,
        },
        {
            'id': '01krnmcs4k7dq7c7c3v42npyj1',
            'name': 'Premium Fiber',
            'description': 'High-speed internet for small businesses',
            'price': Decimal("500000.00"),
            'color': '#16a34a',
            'is_active': True,
        },
        {
            'id': '01krnmcs4kyar0gerska50v782',
            'name': 'Enterprise Fiber',
            'description': 'Ultra-high speed internet for enterprises',
            'price': Decimal("1500000.00"),
            'color': '#ef4444',
            'is_active': True,
        },
        {
            'id': '01krnmcs4kgzfp1eg8s9kk8f7d',
            'name': 'Gaming Fiber',
            'description': 'Low latency internet for gaming enthusiasts',
            'price': Decimal("750000.00"),
            'color': '#f59e0b',
            'is_active': True,
        },
    ]

    records = []
    for item in packages_data:
        records.append(upsert_by_id(db, Package, item))

    db.commit()
    return records


def create_coverages(db):
    coverages_data = [
        {
            'id': '01krnn8mfg7wsvneabckr9z005',
            'area': 'Palmerah',
            'current_customer': 0,
            'max_customer': 13,
            'location': 'SRID=4326;POLYGON ((106.7869454071043 -6.189127709382576, 106.79003531188948 -6.189981012884845, 106.7924385711668 -6.190109008291319, 106.79664427490216 -6.189938347742453, 106.79703051300031 -6.1951861343946755, 106.79754549713117 -6.197148707870309, 106.79904753417951 -6.201756460382421, 106.79707342834455 -6.203377697061766, 106.79630095214827 -6.205596223384565, 106.79600054473859 -6.207260111997165, 106.7928677246092 -6.207516094394228, 106.79080778808576 -6.207174784503854, 106.78990656585677 -6.207558758114987, 106.78921992034896 -6.208156049842657, 106.78874785156232 -6.207985395132424, 106.78784662933333 -6.206961465710062, 106.78334051818831 -6.206534827863365, 106.7823963806151 -6.1952714638279724, 106.78248221130355 -6.193308883372294, 106.78492838592511 -6.193308883372294, 106.7869454071043 -6.189127709382576))',
            'is_active': True,
        },
        {
            'id': '01krnmpmsm11r59esdpfngem4s',
            'area': 'Matraman',
            'current_customer': 2,
            'max_customer': 15,
            'location': 'SRID=4326;POLYGON ((106.85457998962387 -6.199377926495758, 106.85689741821275 -6.1974153613116005, 106.86114603729233 -6.1945568293977065, 106.86406428070052 -6.193106225191936, 106.86921412200911 -6.19238092159449, 106.87273318023665 -6.192252926738594, 106.87453562469466 -6.192466251481181, 106.8729048416136 -6.201767126429159, 106.87363440246564 -6.2079960610530724, 106.87372023315413 -6.214779543049343, 106.86706835479721 -6.215376826584388, 106.86174685211168 -6.213243667988841, 106.85822779388414 -6.20518025041009, 106.85724074096666 -6.202407088858881, 106.85457998962387 -6.199377926495758))',
            'is_active': True,
        },
        {
            'id': '01krnnf6pn4h64zpd0wmnpag06',
            'area': 'Perumahan Jaya Baya',
            'current_customer': 1,
            'max_customer': 1,
            'location': 'SRID=4326;POLYGON ((106.86173612327549 -6.213670300400047, 106.8659847423552 -6.21556881043415, 106.8671005413054 -6.217573970895909, 106.86748677940363 -6.218896519356877, 106.86467582435597 -6.219280484416007, 106.86424667091356 -6.217573970895909, 106.86409646720873 -6.216507397133802, 106.86371022911058 -6.215824788791055, 106.86270171852094 -6.214928863997021, 106.86173612327549 -6.213670300400047))',
            'is_active': True,
        },
        {
            'id': '01krnn3t88zmzf2kbdqgqmvfxw',
            'area': 'Cikini',
            'current_customer': 1,
            'max_customer': 1,
            'location': 'SRID=4326;POLYGON ((106.83629805297832 -6.187570426938418, 106.836598460388 -6.187698422928842, 106.83739239425644 -6.189021046347812, 106.8387656852721 -6.1927542397474085, 106.84011751861564 -6.196594068280251, 106.83915192337025 -6.197191372430214, 106.83872276992786 -6.196636732884798, 106.83698469848616 -6.196338080580441, 106.83687741012555 -6.194951478382045, 106.83623367996196 -6.19187960823206, 106.83625513763408 -6.191004975268199, 106.83629805297832 -6.187570426938418))',
            'is_active': True,
        },
        {
            'id': '01krnngmry9nwa62hnycc8g579',
            'area': 'Rawa Bunga',
            'current_customer': 2,
            'max_customer': 3,
            'location': 'SRID=4326;POLYGON ((106.86658555717462 -6.215824788791043, 106.86858112068177 -6.215739462685916, 106.87267953605664 -6.215419489668439, 106.87282973976146 -6.216806038005197, 106.87400991172805 -6.218277908394025, 106.8742674037935 -6.221541606298243, 106.8742674037935 -6.224463985262798, 106.87366658897413 -6.224613303459537, 106.87231475563061 -6.224421322913074, 106.87117749900825 -6.224421322913074, 106.86787301750182 -6.224293335843113, 106.86838800163268 -6.2231414508104566, 106.86828071327209 -6.220283058526208, 106.86761552543638 -6.217936605482298, 106.86658555717462 -6.215824788791043))',
            'is_active': True,
        },
        {
            'id': '01krnmmg5ytmenk7x7yyy9tqd0',
            'area': 'Rawamangun',
            'current_customer': 1,
            'max_customer': 25,
            'location': 'SRID=4326;POLYGON ((106.87547976226794 -6.192764905976049, 106.88603693695053 -6.1937035332887636, 106.90187269897444 -6.193831527793017, 106.90333182067856 -6.193575538753455, 106.90539175720198 -6.192551581354119, 106.90461928100571 -6.200487199239513, 106.90436178894028 -6.201980447325386, 106.9023876831053 -6.206033527951679, 106.90045649261461 -6.213243667988841, 106.89157301635728 -6.213030351653707, 106.88835436553941 -6.213712963621803, 106.8876677200316 -6.213968942881591, 106.87470728607167 -6.214864869310139, 106.87414938659656 -6.2057348809692945, 106.87354857177722 -6.2023644247210745, 106.87432104797351 -6.197074044882159, 106.87547976226794 -6.192764905976049))',
            'is_active': True,
        },
        {
            'id': '01krnmzr0t8jajg4m4mqaf6net',
            'area': 'Kebon Sirih',
            'current_customer': 2,
            'max_customer': 3,
            'location': 'SRID=4326;POLYGON ((106.82348782272331 -6.183581203034522, 106.83353001327507 -6.182941217788429, 106.83507496566763 -6.185117164465059, 106.83606201858511 -6.186567790607751, 106.83374458999623 -6.1865251251897835, 106.83241421432484 -6.186866448437088, 106.83086926193226 -6.187165106097651, 106.82992512435902 -6.186781117645922, 106.82348782272328 -6.186823783043229, 106.82348782272331 -6.183581203034522))',
            'is_active': True,
        },
        {
            'id': '01krnna05bfgk5zss9bn4kkaer',
            'area': 'Jalan Batusari',
            'current_customer': 2,
            'max_customer': 3,
            'location': 'SRID=4326;POLYGON ((106.78350145072929 -6.188221072901326, 106.78540045471188 -6.18859439399374, 106.78656989784241 -6.188925049598188, 106.78466016502374 -6.192978230512218, 106.78226763458241 -6.193212887402033, 106.78243929595936 -6.190908978879059, 106.78290063590994 -6.189533028717948, 106.78327614517202 -6.188711723425446, 106.7833405181884 -6.188306403460006, 106.78350145072929 -6.188221072901326))',
            'is_active': True,
        },
        {
            'id': '01krnncabzjyvtq86k3x4qt4af',
            'area': 'Jalan Bima',
            'current_customer': 1,
            'max_customer': 1,
            'location': 'SRID=4326;POLYGON ((106.78341562004081 -6.185479821373828, 106.78420955390925 -6.185341158467457, 106.78514296264645 -6.185309159330062, 106.78728872985842 -6.185309159330062, 106.78711706848148 -6.1875917596056915, 106.78663427085877 -6.188690390803464, 106.78351217956536 -6.188018412769292, 106.78347999305717 -6.187581093272169, 106.78355509490959 -6.186535791544539, 106.78347999305717 -6.186226467167541, 106.78341562004081 -6.185479821373828))',
            'is_active': True,
        },
        {
            'id': '01krnmxffef47pqsd3a1arrkkg',
            'area': 'Setia Budi',
            'current_customer': 3,
            'max_customer': 15,
            'location': 'SRID=4326;POLYGON ((106.82305866928037 -6.203367031046961, 106.83704907150204 -6.206012196030017, 106.84520298690728 -6.208828002226342, 106.84305721969537 -6.214630222059669, 106.84704834670953 -6.223034794660653, 106.84425884933404 -6.224186679927118, 106.83370167465144 -6.2254238872149275, 106.8319850608819 -6.225509211748058, 106.82447487564022 -6.223333431824067, 106.8223291084283 -6.2224801823354285, 106.82099873275693 -6.221242968116058, 106.81996876449524 -6.218896519356444, 106.81872421951235 -6.215056853346422, 106.8219428703302 -6.209382628945052, 106.82305866928037 -6.203367031046961))',
            'is_active': True,
        },
    ]

    records = []
    for item in coverages_data:
        records.append(upsert_by_id(db, Coverage, item))

    db.commit()
    return records


def create_fiber_optics(db):
    fiber_optics_data = [
        {
            'id': '01krpb4ydyazws4crc0hc2ppmh',
            'segment_id': '01krnmcs3s3ntrsswm27fv4dtq',
            'operator_id': '01krnmcs49c6k2948f4b9dhvny',
            'location': 'SRID=4326;LINESTRING(106.85852820129405 -6.196412743671832, 106.86234766693126 -6.209126647455071, 106.86736876220712 -6.208657347733748, 106.86955744476329 -6.20925463821557, 106.87140280456553 -6.206396170488386, 106.8717032119752 -6.204177647533172, 106.87565142364511 -6.204348303476697)',
            'is_active': True,
        },
        {
            'id': '01krpb683j40qmzjpxvn0nqxe9',
            'segment_id': '01krnmcs3s3ntrsswm27fv4dtq',
            'operator_id': '01krnmcs49c6k2948f4b9dhvny',
            'location': 'SRID=4326;LINESTRING(106.87565142364512 -6.204348303476683, 106.87569433898938 -6.205457565762584, 106.87869841308604 -6.2056282212916445, 106.87869841308604 -6.202215100211481, 106.88084418029796 -6.201873786887978, 106.88603693695077 -6.2021297719013, 106.90371805877692 -6.20276973389086)',
            'is_active': True,
        },
        {
            'id': '01krpb71dsjrc9t6rj5an8a0y8',
            'segment_id': '01krnmcs3s3ntrsswm27fv4dtq',
            'operator_id': '01krnmcs49c6k2948f4b9dhvny',
            'location': 'SRID=4326;LINESTRING(106.88620859832774 -6.193724865708234, 106.88599402160655 -6.206780144667007, 106.89007097930917 -6.206524161912361, 106.89127260894784 -6.210449217146826, 106.88938433380136 -6.211985100361685, 106.88788229675302 -6.213947611281305)',
            'is_active': True,
        },
        {
            'id': '01krpb7g5bvmcth27r3cvmfcd1',
            'segment_id': '01krnmcs3s3ntrsswm27fv4dtq',
            'operator_id': '01krnmcs49c6k2948f4b9dhvny',
            'location': 'SRID=4326;LINESTRING(106.8912296936036 -6.210449217146826, 106.89371878356943 -6.209979918604179, 106.89689451904306 -6.212027763720358, 106.89826781005866 -6.2128383668780724, 106.90062815399176 -6.212753040288675)',
            'is_active': True,
        },
        {
            'id': '01krpb8qkvs040mr3vk130b8w6',
            'segment_id': '01krnmcs3s3ntrsswm27fv4dtq',
            'operator_id': '01krnmcs49cv8cgch9njt8pkc0',
            'location': 'SRID=4326;LINESTRING(106.88423449249278 -6.193596871178117, 106.88384825439464 -6.195218132933363, 106.88281828613292 -6.196668731335409, 106.8829041168214 -6.203793671458203, 106.8817883178712 -6.20468961519795, 106.8817883178712 -6.206609489511064, 106.88367659301768 -6.206908135997702, 106.88320452423106 -6.20925463821557, 106.88401991577159 -6.209211974632172, 106.88410574646005 -6.211686456754173, 106.8883972808839 -6.211857110264917, 106.88813978881845 -6.2128810301675745, 106.88719565124521 -6.2133076628724595, 106.87891298980723 -6.213990274480873, 106.8766384765626 -6.2147155483446115, 106.87475020141615 -6.21475821148193)',
            'is_active': True,
        },
        {
            'id': '01krpba4cp867yp7y3mdn418r8',
            'segment_id': '01krnmcs3sn64a091hqrqdy96p',
            'operator_id': '01krnmcs499nht3j4xndf3h70q',
            'location': 'SRID=4326;LINESTRING(106.86239058227551 -6.209169311045352, 106.86303431243908 -6.211046505596172, 106.86101729125988 -6.211643793367855, 106.86178976745617 -6.213435652616491, 106.86277682037367 -6.212753040288675, 106.8637209579469 -6.213435652616491, 106.8637209579469 -6.213990274480886, 106.86500841827404 -6.21458755891188, 106.86487967224134 -6.215824788790636)',
            'is_active': True,
        },
        {
            'id': '01krpbfw9s0kcbkejhxxy0ky0q',
            'segment_id': '01krnmcs3s3ntrsswm27fv4dtq',
            'operator_id': '01krnmcs49aa0df7jqrdy1p697',
            'location': 'SRID=4326;LINESTRING(106.87593573780082 -6.211281154444399, 106.87245959491743 -6.211153164176492, 106.87269562931074 -6.214694216774718, 106.8726527139665 -6.216400739638331, 106.87278145999922 -6.2177232910496825, 106.87110776157391 -6.2177232910496825, 106.87125796527872 -6.219643117825183, 106.87162274570476 -6.219685780562795, 106.87162274570476 -6.220368383893789, 106.8721162721635 -6.220539034588063, 106.87250251026167 -6.221968231977397, 106.86979884357459 -6.222074888343173, 106.86898345203403 -6.220048413692757, 106.87067860813148 -6.219685780562795, 106.87042111606607 -6.2184272283478945, 106.86838263721468 -6.218512554017005, 106.86797494144442 -6.217445982158333, 106.86870450229648 -6.21667804908077, 106.87027091236122 -6.216486065636184, 106.87037820072183 -6.216934026897858)',
            'is_active': True,
        },
        {
            'id': '01krpbm5h1z1hn1rjjzm9cdetk',
            'segment_id': '01krnmcs3sn64a091hqrqdy96p',
            'operator_id': '01krnmcs49e5mqqmkpmentck5p',
            'location': 'SRID=4326;LINESTRING(106.83985309765085 -6.196651359107407, 106.83852272197944 -6.194720782351488, 106.83807211086493 -6.194838110422158, 106.83782534763554 -6.19424080360899, 106.83732109234076 -6.193611497485417, 106.83794336483223 -6.1931315177343915)',
            'is_active': True,
        },
        {
            'id': '01krpbpsmjwnbxa87xbax89e2v',
            'segment_id': '01krnmcs3sgz7xgyp3yvgdrzg3',
            'operator_id': '01krnmcs49ynp6p60smsdvnh5p',
            'location': 'SRID=4326;LINESTRING(106.83031516239372 -6.187051736466688, 106.8322892682287 -6.185302453107795, 106.83253603145809 -6.1863264245569765, 106.83373766109679 -6.186070431880641, 106.8336625592444 -6.185185122919243, 106.83328704998227 -6.1844918076372775, 106.83261113331051 -6.185046459935573, 106.8323750989172 -6.183585163204527, 106.83177428409785 -6.183467832634933, 106.83106618091789 -6.18359582961867, 106.83065848514761 -6.183659828098911, 106.83037953541006 -6.184513140428746, 106.82953195736135 -6.184534473219349, 106.82921009227954 -6.185291786728078, 106.82902770206651 -6.18592110276217)',
            'is_active': True,
        },
        {
            'id': '01krpbqhc69nhj9krekxhazpbf',
            'segment_id': '01krnmcs3s3ntrsswm27fv4dtq',
            'operator_id': '01krnmcs4938xg4t6zx2w82vh6',
            'location': 'SRID=4326;LINESTRING(106.82356672451206 -6.184406476462805, 106.82485418483924 -6.184267813274956, 106.8250580327244 -6.185345118624422, 106.82562666103554 -6.185387784137654, 106.82592706844522 -6.18424648047359, 106.82733254596907 -6.184769133859165)',
            'is_active': True,
        },
        {
            'id': '01krpbtrcvfqjhhxt392r1g18x',
            'segment_id': '01krnmcs3s3ntrsswm27fv4dtq',
            'operator_id': '01krnmcs49c6k2948f4b9dhvny',
            'location': 'SRID=4326;LINESTRING(106.78714064448073 -6.186760125525842, 106.78520945398995 -6.186621462955313, 106.78522018282601 -6.186226807747811, 106.7840721973676 -6.186280139549808)',
            'is_active': True,
        },
        {
            'id': '01krpbv8fdmras7ywfyt7ew3p9',
            'segment_id': '01krnmcs3s3ntrsswm27fv4dtq',
            'operator_id': '01krnmcs499nht3j4xndf3h70q',
            'location': 'SRID=4326;LINESTRING(106.78539184420296 -6.188616067198359, 106.78520945398995 -6.18970402997577, 106.78440479128545 -6.18973602884708, 106.78430823176093 -6.190205345403486)',
            'is_active': True,
        },
        {
            'id': '01krpbw2teasxh6y2ejbbwbpwh',
            'segment_id': '01krnmcs3s3ntrsswm27fv4dtq',
            'operator_id': '01krnmcs49e5mqqmkpmentck5p',
            'location': 'SRID=4326;LINESTRING(106.78523091166207 -6.189725362556851, 106.7853274711866 -6.189810692872574, 106.78530601351449 -6.190642662728531, 106.7849305042524 -6.190621330184472, 106.78494123308845 -6.190855988121529, 106.78377178995792 -6.190941318254612, 106.78372887461369 -6.191847950067277)',
            'is_active': True,
        },
        {
            'id': '01krpc2fnpnqhsef3mfvs4rcmz',
            'segment_id': '01krnmcs3s3ntrsswm27fv4dtq',
            'operator_id': '01krnmcs49ynp6p60smsdvnh5p',
            'location': 'SRID=4326;LINESTRING(106.79391054003447 -6.19007735002, 106.79363159029694 -6.190567998820234, 106.79303077547759 -6.190738659165672, 106.79251579134669 -6.191805285075313, 106.79227975695339 -6.192807911466162, 106.79247287600245 -6.193554546903505, 106.79238704531397 -6.194322513680357, 106.79380325167389 -6.195197141148817, 106.79418948977204 -6.195858443882338, 106.79376033632964 -6.196861062575226, 106.7933955559036 -6.197309040524406, 106.79343847124784 -6.198013005104665, 106.79388908236237 -6.19871696874563, 106.79416803209992 -6.199719582006411, 106.79382470934601 -6.200295550464557, 106.79326680987089 -6.201511481810439, 106.79255870669095 -6.202962062906044, 106.79285911410062 -6.204284648073271, 106.79260162203518 -6.20522325488824, 106.79251579134672 -6.20739910971087)',
            'is_active': True,
        },
        {
            'id': '01krpc3p8rs91mxpq8eedpyjtt',
            'segment_id': '01krnmcs3s3ntrsswm27fv4dtq',
            'operator_id': '01krnmcs49cv8cgch9njt8pkc0',
            'location': 'SRID=4326;LINESTRING(106.79843810885163 -6.202130112471725, 106.79826644747466 -6.201106171673396, 106.7975368866226 -6.201212832265977, 106.79727939455717 -6.200807521899323, 106.79693607180326 -6.200487539810865, 106.79573444216454 -6.200423543369882, 106.79543403475489 -6.2005515362441015, 106.79502633898458 -6.2005088719561465, 106.79476884691914 -6.200359546921138, 106.79451135485373 -6.200423543369882, 106.79442552416523 -6.200615532669564, 106.79367450564105 -6.200658196948879, 106.79339555590349 -6.201127503793627, 106.79204372255995 -6.2005088719561465, 106.79288057177263 -6.198930290875645, 106.79225829928116 -6.198524978754941, 106.7916574844618 -6.198439649847733, 106.79088500826549 -6.200359546921138, 106.7905631431837 -6.200722193361391, 106.79024127810192 -6.201298160724535, 106.78968337862678 -6.2024287614966624, 106.78822425692265 -6.202044784147805, 106.78783801882449 -6.200871518293731, 106.78712991564454 -6.200572868386774, 106.78277400820424 -6.200914182552335)',
            'is_active': True,
        },
        {
            'id': '01krpc5a789dez4jc4mdtzevfe',
            'segment_id': '01krnmcs3s3ntrsswm27fv4dtq',
            'operator_id': '01krnmcs49aa0df7jqrdy1p697',
            'location': 'SRID=4326;LINESTRING(106.78230193941761 -6.195559791137602, 106.7836966881054 -6.195815779214906, 106.78378251879387 -6.195495794098865, 106.78425458758049 -6.195538458792213, 106.78434041826898 -6.195175808788837, 106.78530601351437 -6.195431797052381, 106.7864432701367 -6.1954531294020825, 106.78652910082519 -6.196967724026226, 106.78931859820077 -6.197010388600583, 106.78912547915168 -6.1988236298214385, 106.78994087069223 -6.19920760951565, 106.78944734423345 -6.199975568065512, 106.7907777199049 -6.200743525497168, 106.7912283310194 -6.201106171673396, 106.79129270403575 -6.201810131185848, 106.7923012146254 -6.201895459547743, 106.79260162203506 -6.20070086122476, 106.79200080721571 -6.200487539810865, 106.79219392626479 -6.200146225369182, 106.79290202944475 -6.200572868386774, 106.79361013262469 -6.1993782670677975, 106.79318097918228 -6.197991672858496, 106.79303077547746 -6.1970317208864705, 106.79139999239636 -6.196519745787286, 106.79142145006848 -6.196263758051459, 106.79206518023207 -6.194983817509705, 106.79249433367445 -6.194770493784323, 106.7918935188551 -6.193789203537222, 106.7918935188551 -6.1918906150550805, 106.7915501961012 -6.1918906150550805, 106.79172185747815 -6.191357302455668, 106.79148582308486 -6.190098682586056)',
            'is_active': True,
        },
        {
            'id': '01krpc62p66kjqb0hpr9k6kfbc',
            'segment_id': '01krnmcs3s3ntrsswm27fv4dtq',
            'operator_id': '01krnmcs49c6k2948f4b9dhvny',
            'location': 'SRID=4326;LINESTRING(106.82792095034308 -6.204348644045581, 106.82963756411262 -6.207335114109058, 106.83036712496465 -6.20980960505033, 106.8305387863416 -6.213052023854303, 106.830967939784 -6.217488985634454, 106.83191207735723 -6.220560706479101, 106.83311370699592 -6.225296240944517)',
            'is_active': True,
        },
        {
            'id': '01krpc7042zyzn77ewzhr4s74s',
            'segment_id': '01krnmcs3s3ntrsswm27fv4dtq',
            'operator_id': '01krnmcs4938xg4t6zx2w82vh6',
            'location': 'SRID=4326;LINESTRING(106.82036784975715 -6.212284084363519, 106.82161239474004 -6.212753380852139, 106.82461646883672 -6.212625390942198, 106.82461646883672 -6.213094687126489, 106.82594684450811 -6.213009360578668, 106.82800678103155 -6.215185183226756, 106.82972339480108 -6.214886541435215, 106.82972339480108 -6.213435993179498, 106.83259872286504 -6.214843878308303, 106.83474449007697 -6.213137350395229, 106.83620361178104 -6.214033278239644, 106.83723358004276 -6.213265340180671, 106.83804897158332 -6.214459910010401, 106.838177717616 -6.2106202116234765, 106.84049514620489 -6.211132173026671, 106.84049514620489 -6.2119427775635385, 106.84251216738409 -6.212369411028945, 106.84307006685917 -6.214673225766038)',
            'is_active': True,
        },
        {
            'id': '01krpc829qmg5wcwjv83v86yme',
            'segment_id': '01krnmcs3s3ntrsswm27fv4dtq',
            'operator_id': '01krnmcs499nht3j4xndf3h70q',
            'location': 'SRID=4326;LINESTRING(106.83538822024055 -6.225253578662361, 106.83538822024055 -6.219408813265372, 106.83607486574836 -6.21616643363395, 106.83611778109257 -6.213990615043562, 106.83208373873418 -6.212241421025622, 106.83079627840704 -6.211089509595444, 106.83079627840704 -6.2106202116234765, 106.83208373873418 -6.210662875092769, 106.83324245302862 -6.209681614424699, 106.83212665407844 -6.208316379149169, 106.83375743715949 -6.206524502479859, 106.83397201388067 -6.2054152424399005)',
            'is_active': True,
        },
    ]

    records = []
    for item in fiber_optics_data:
        records.append(upsert_by_id(db, FiberOptic, item))

    db.commit()
    return records


def create_package_coverages(db):
    """network_data.sql has no package_coverages records, so keep this empty."""
    return []


def create_customers(db):
    customers_data = [
        {
            'id': '01krpbdxfdk2ay5avr335dzwdy',
            'code': 'CUST01',
            'name': 'majujaya@app.com',
            'email': 'majujaya@app.com',
            'phone': '123456789',
            'province': '',
            'city': '',
            'district': '',
            'subdistrict': '',
            'postcode': '',
            'address': 'Jl. Pasar Utara No. 1',
            'location': 'SRID=4326;POINT (106.864912 -6.215883)',
            'package_id': '01krnmcs4kyar0gerska50v782',
            'price': Decimal("3500000.00"),
            'is_active': True,
        },
        {
            'id': '01krpbh342wbwa3veh3dp2q5a9',
            'code': 'CUST02',
            'name': 'Pak Joko',
            'email': 'joko@app.com',
            'phone': '123456789',
            'province': '',
            'city': '',
            'district': '',
            'subdistrict': '',
            'postcode': '',
            'address': 'St. Jatinegara No. 35',
            'location': 'SRID=4326;POINT (106.870507 -6.217083)',
            'package_id': '01krnmcs4kge63eg4nza0ek2cw',
            'price': Decimal("250000.00"),
            'is_active': True,
        },
        {
            'id': '01krpbjkc6fs9mwbxb029kmj7e',
            'code': 'CUST03',
            'name': 'Pak Mulyo',
            'email': 'mulyo@app.com',
            'phone': '123456789',
            'province': '',
            'city': '',
            'district': '',
            'subdistrict': '',
            'postcode': '',
            'address': 'Jl. Masjid Jatinegara No. 5',
            'location': 'SRID=4326;POINT (106.871387 -6.219707)',
            'package_id': '01krnmcs4k7dq7c7c3v42npyj1',
            'price': Decimal("500000.00"),
            'is_active': True,
        },
        {
            'id': '01krpbn5gajd6ahfxvhgw6h6v4',
            'code': 'CUST04',
            'name': 'PT Duta Merdeka',
            'email': 'duta@app.com',
            'phone': '123456789',
            'province': '',
            'city': '',
            'district': '',
            'subdistrict': '',
            'postcode': '',
            'address': 'Jl. Cikini No. 5',
            'location': 'SRID=4326;POINT (106.838018 -6.193206)',
            'package_id': '01krnmcs4kyar0gerska50v782',
            'price': Decimal("2500000.00"),
            'is_active': True,
        },
        {
            'id': '01krpbrgdzax6h72r1mq0w3vbc',
            'code': 'CUST05',
            'name': 'Mang Ujang',
            'email': 'ujang@app.com',
            'phone': '123456789',
            'province': '',
            'city': '',
            'district': '',
            'subdistrict': '',
            'postcode': '',
            'address': 'Jl. Kebon Sirih No. 2',
            'location': 'SRID=4326;POINT (106.827397 -6.184854)',
            'package_id': '01krnmcs4kgzfp1eg8s9kk8f7d',
            'price': Decimal("850000.00"),
            'is_active': True,
        },
        {
            'id': '01krpbsmzbkh833wjkj4zsjhse',
            'code': 'CUST06',
            'name': 'PT Mekar Jaya',
            'email': 'mekar@app.com',
            'phone': '123456789',
            'province': '',
            'city': '',
            'district': '',
            'subdistrict': '',
            'postcode': '',
            'address': 'Jl. Jaksa No. 83',
            'location': 'SRID=4326;POINT (106.829092 -6.185996)',
            'package_id': '01krnmcs4kyar0gerska50v782',
            'price': Decimal("1250000.00"),
            'is_active': True,
        },
        {
            'id': '01krpbxm3ktj2e1146fdzcg87g',
            'code': 'CUST07',
            'name': 'Neng Ira',
            'email': 'ira@app.com',
            'phone': '123456789',
            'province': '',
            'city': '',
            'district': '',
            'subdistrict': '',
            'postcode': '',
            'address': 'Jl. Batusari No. 1',
            'location': 'SRID=4326;POINT (106.784373 -6.190291)',
            'package_id': '01krnmcs4k7dq7c7c3v42npyj1',
            'price': Decimal("550000.00"),
            'is_active': True,
        },
        {
            'id': '01krpbz2tzra0m5nek20hj77q4',
            'code': 'CUST08',
            'name': 'Bang Choky',
            'email': 'choky@app.com',
            'phone': '123456789',
            'province': '',
            'city': '',
            'district': '',
            'subdistrict': '',
            'postcode': '',
            'address': 'Jl. PLN No. 1',
            'location': 'SRID=4326;POINT (106.783804 -6.191912)',
            'package_id': '01krnmcs4kge63eg4nza0ek2cw',
            'price': Decimal("225000.00"),
            'is_active': True,
        },
        {
            'id': '01krpc0zddgmrap405ngn8z9vf',
            'code': 'CUST09',
            'name': 'PT Mencari Cinta Sejati',
            'email': 'mcs@app.com',
            'phone': '123456789',
            'province': '',
            'city': '',
            'district': '',
            'subdistrict': '',
            'postcode': '',
            'address': 'Jl. Mencari Cinta Sejati No. 2000',
            'location': 'SRID=4326;POINT (106.784147 -6.186333)',
            'package_id': '01krnmcs4kyar0gerska50v782',
            'price': Decimal("13000000.00"),
            'is_active': True,
        },
        {
            'id': '01krpcbg693msyjj8vgb9b2czh',
            'code': 'CUST10',
            'name': 'Mas Dani',
            'email': 'dani@app.com',
            'phone': '123456789',
            'province': '',
            'city': '',
            'district': '',
            'subdistrict': '',
            'postcode': '',
            'address': 'Jl. Pal Merah No. 3',
            'location': 'SRID=4326;POINT (106.860795 -6.203832)',
            'package_id': '01krnmcs4kge63eg4nza0ek2cw',
            'price': Decimal("125000.00"),
            'is_active': True,
        },
        {
            'id': '01krpcczt5ne04g2546pr95rh8',
            'code': 'CUST11',
            'name': 'Mas Agung',
            'email': 'agung@app.com',
            'phone': '123456789',
            'province': '',
            'city': '',
            'district': '',
            'subdistrict': '',
            'postcode': '',
            'address': 'Jl. Pal Merah No. 5',
            'location': 'SRID=4326;POINT (106.861482 -6.206072)',
            'package_id': '01krnmcs4k7dq7c7c3v42npyj1',
            'price': Decimal("250000.00"),
            'is_active': True,
        },
        {
            'id': '01krpcjdb3de27wcq81ekeygcv',
            'code': 'CUST12',
            'name': 'Mas Agung',
            'email': 'agungz@app.com',
            'phone': '123456789',
            'province': '',
            'city': '',
            'district': '',
            'subdistrict': '',
            'postcode': '',
            'address': 'Jl. Pal Merah No. 5',
            'location': 'SRID=4326;POINT (106.861439 -6.206019)',
            'package_id': '01krnmcs4kgzfp1eg8s9kk8f7d',
            'price': Decimal("500000.00"),
            'is_active': True,
        },
        {
            'id': '01krpckrzjs0363jjw4ghfyqx2',
            'code': 'CUST13',
            'name': 'Bang Jago',
            'email': 'jago@app.com',
            'phone': '123456789',
            'province': '',
            'city': '',
            'district': '',
            'subdistrict': '',
            'postcode': '',
            'address': 'Jl. Jago No. 1',
            'location': 'SRID=4326;POINT (106.886212 -6.202232)',
            'package_id': '01krnmcs4kge63eg4nza0ek2cw',
            'price': Decimal("100000.00"),
            'is_active': True,
        },
        {
            'id': '01krpcn7xay2jdc0jz17b09qjw',
            'code': 'CUST14',
            'name': 'Ibu Imah',
            'email': 'imah@app.com',
            'phone': '123456789',
            'province': '',
            'city': '',
            'district': '',
            'subdistrict': '',
            'postcode': '',
            'address': 'Jl. Imah No. 2',
            'location': 'SRID=4326;POINT (106.834853 -6.213218)',
            'package_id': '01krnmcs4kge63eg4nza0ek2cw',
            'price': Decimal("100000.00"),
            'is_active': True,
        },
        {
            'id': '01krpcpg4f0kyfpyzjftfhw5hw',
            'code': 'CUST15',
            'name': 'Ibu Ema',
            'email': 'ema@app.com',
            'phone': '123456789',
            'province': '',
            'city': '',
            'district': '',
            'subdistrict': '',
            'postcode': '',
            'address': 'Jl. Ema No. 9',
            'location': 'SRID=4326;POINT (106.824778 -6.213133)',
            'package_id': '01krnmcs4k7dq7c7c3v42npyj1',
            'price': Decimal("200000.00"),
            'is_active': True,
        },
        {
            'id': '01krpcqmctecbmtktqk1n3g29g',
            'code': 'CUST16',
            'name': 'Pak Eno',
            'email': 'eno@app.com',
            'phone': '123456789',
            'province': '',
            'city': '',
            'district': '',
            'subdistrict': '',
            'postcode': '',
            'address': 'Jl. Eno No. 6',
            'location': 'SRID=4326;POINT (106.829842 -6.20748)',
            'package_id': '01krnmcs4kgzfp1eg8s9kk8f7d',
            'price': Decimal("500000.00"),
            'is_active': True,
        },
    ]

    records = []
    for item in customers_data:
        records.append(upsert_by_id(db, Customer, item))

    db.commit()
    return records


def main():
    print("Starting network data seeding...")

    db = SessionLocal()

    try:
        # Enable PostGIS extension only. Table schema still comes from the models.
        from sqlalchemy import text
        db.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        db.commit()

        # Create tables from the existing SQLAlchemy models, same pattern as the original seeder.
        BaseModel.metadata.create_all(bind=engine)
        print("Database tables created successfully")

        print("Creating segments...")
        segments = create_segments(db)

        print("Creating operators...")
        operators = create_operators(db)

        print("Creating packages...")
        packages = create_packages(db)

        print("Creating coverages...")
        coverages = create_coverages(db)

        print("Creating fiber optics...")
        fiber_optics = create_fiber_optics(db)

        print("Creating package-coverages...")
        package_coverages = create_package_coverages(db)

        print("Creating customers...")
        customers = create_customers(db)

        print("\n=== Seeding Summary ===")
        print(f"Segments: {len(segments)}")
        print(f"Operators: {len(operators)}")
        print(f"Packages: {len(packages)}")
        print(f"Coverages: {len(coverages)}")
        print(f"Fiber Optics: {len(fiber_optics)}")
        print(f"Package Coverages: {len(package_coverages)}")
        print(f"Customers: {len(customers)}")
        print("\nNetwork data seeding completed successfully!")

    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
