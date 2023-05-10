# Generalized Petersen Graph

dokumentaciu je mozne vidiet aj na: https://github.com/kripso/graph-algorithms

![](assets/Pasted%20image%2020230509092647.png)

# Process

## Logicky Postup
![](assets/Pasted%20image%2020230509093312.png)
ked zoberieme predpis vseobecneho petersonovho grafu, mozeme videt ze akukolvek cestu alebo cyklus nacrtneme ok ktorehokolvek bodu. Vieme tuto to istu cestu alebo cysklus zopakovan *n* krat alebo ked zapocitam aj zrkadlovu cestu tak `n*2` krat. Preto su vieme urychlit vypocet hamiltonovskych ciest a cyklov podla jednoduchej strategie kde si zoberie 4 zaciatky -> 
* cesta zacinajuca z vnutra a pokracujuce na vonkajsiu kruznicu
* cesta zacinajuca z vnutra a pokracujuce v nutornej casti
* cesta zacinajuca na vonkajsej kruznici a pokracujuca v nej
* cesta zacinajuca na vonkajsej kruznici a pokracujuca dnu

### Tvorba pociatocnej trasi
samotna tvorba tychto troch zaciatkov je jednoducha nakolko n nam reprezentuje velkost vonkajej kruznici ale indexujeme od 0 takze vsetky vnutorne body su n az `n*2 - 1` a vonkajsia kruznica sa sklada z bodov 0 az `n-1`
```python
in_in = (n, n+k)
in_out = (n, 0)
out_in = (0, n)
out_out = (0, 1)
```

## Nasobok moznych hamiltonovskych ciest a cyklov
nakolko petersenov graf vieme pomyselne rotovat, akonahle vypocitame pocet ciest a cyklov pre ktorykolvek z hore spomenutych bodov vieme pomocou dole ukazanych nasobkov zistit pocet vsetkych ciest a cyklov ktore by sme spravili keby proces vyhladavanie skusame pre vsetky body.
```
out_out -> 2*n
0,1 | 1,0 | 2,1
0,2 | 1,2 | 2,0

out_in -> n 
0,3 | 1,4 | 2,5

in_out -> n 
3,0 | 4,1 | 5,2

in_in -> 2*n 
3,4 | 4,3 | 5,3
3,5 | 4,5 | 5,4
```

## Zakladna logika
ako zaklad mam classu Traversable_Graph ktora sluzi ako zakladna ktora reprezentuje instaciu vseobecneho petersenoveho grafu s aktualne prejdenou cestou.

dalej obsahuje funkciu move ktora sa stara o prechadzanie samim sebou.
```python
from dataclasses import dataclass, field
from copy import deepcopy
import numpy as np

@dataclass
class Traversable_Graph():
    path: list[int] = field(default_factory=list, init=False)
    position: tuple = field(default_factory=tuple, init=False)
    initial_position: int =  field(default_factory=int, init=False)
    end_positions: list[int] =  field(default_factory=list[int], init=False)
    next_moves: list[tuple()] = field(default_factory=list[tuple()])
    possible_moves: list[tuple()] = field(default_factory=list[tuple()])
    n: int = field(default_factory=int)
    k: int = field(default_factory=int)

    def __post_init__(self):
        self.initial_position = self.next_moves[0]
        if self.initial_position[0] != 0:
            self.end_positions = [0, self.n+self.k, (self.n * 2) - self.k]
        if self.initial_position[0] == 0:
            self.end_positions= [1, self.n-1, self.n]

    def end(self):
        new_move = deepcopy(self)
        new_move.path.append(new_move.initial_position[0])
        return new_move

    def move(self, position: tuple = None, end = False):
        new_move = deepcopy(self)
        assert (position[1] not in new_move.path)

        if len(new_move.path) == 0:
            new_move.path.append(position[0])
    
        tmp_possible_moves = []
        for index, move_set in enumerate(new_move.possible_moves):
            tmp_possible_moves.append([])
            for move in move_set:
                if move[0] not in new_move.path and move[1] not in new_move.path:
                    tmp_possible_moves[index].append(move)

        new_move.possible_moves = tmp_possible_moves
        new_move.path.append(position[1])

        new_move.next_moves = []
        for move_set in new_move.possible_moves:
            for move in move_set:
                if position[1] == move[0]:
                    new_move.next_moves.append(move)

        return new_move

```

### generovanie matice susednosti
pred zaciatkom prechadzania grafu si generujem petersenove grafu pomocou matice susednosti ktora funguje na predpise vseobecneho petersenovho grafu a troch usekoch. spojenia vonkajsieho kruhu kde kazdy bod je o 1 vacsi ako predchadzajuci, spojenia vnutrej casti grafu kde su body vzdialene o velkost *k* a spojenie vonkajsieho a vnutorneho cyklu kde vzdialenost bodov je *n*

```python
def generalized_petersen_adj_matrix(n, k):
    adj_matrix = np.zeros((2 * n, 2 * n), dtype=int)

    for i in range(n):
        # Connect outer cycle nodes
        x_out = i
        y_out = (i + 1) % n
        adj_matrix[x_out, y_out] = 1
        adj_matrix[y_out, x_out] = 1

        # Connect inner cycle nodes
        x_in = n + i
        y_in = n + (i + k) % n
        adj_matrix[x_in, y_in] = 1
        adj_matrix[y_in, x_in] = 1

        # # Connect outer and inner cycle nodes
        adj_matrix[x_out, x_in] = 1
        adj_matrix[x_in, x_out] = 1

    return adj_matrix
```

### Vypocet ciest
Vypocet ciest prebiehal podla hore spomenujet logiky kde kazda cesta s jednym zo zaciatocnych 4 bodov prebiehala na jednom pocitavom jadre. To nam pomohlo zrychly 4 nasobne vypocet moznych ciest plus sme pocitali 4 separatne grafy naraz.

```python
def traverse(move_, target_len):
    paths = []
    for next_move in move_.next_moves:
        paths.extend(traverse(move_.move(next_move), target_len))
    
    if len(move_.path)==target_len:
        return move_.path
    
    return paths

def calculate_path(n, k, move_set, target_len, start_position, multiplier):
    hammilton_paths_count = 0
    paths = traverse(Move(move_set).overwrite_next_moves([start_position]), target_len)
    paths = set(','.join(str(item) for item in paths[i:i+target_len]) for i in range(0, len(paths), target_len))
    hammilton_paths_count += multiplier*len(paths)
    with open(f'./data/graphs/{n=};{k=};{start_position=}.yaml', "w+") as file:
        yaml.dump({"paths": list(paths), 'count': hammilton_paths_count}, file, default_flow_style=False, sort_keys=False)
    return hammilton_paths_count


def calculate_graph(n=9, k=2):
    petersen = generalized_petersen_adj_matrix(n, k)
    move_set, (in_in, in_out, out_in, out_out) = get_move_set(petersen, n, k)
    target_len = n*2
    
    preps = [(in_in, 2*n), (in_out, n), (out_in, n), (out_out, 2*n)]
    
    with ProcessPoolExecutor(max_workers=4) as e:
        futures = [e.submit(calculate_path, n, k, move_set, target_len, *prep) for prep in preps]
        result = [future.result() for future in futures]

    print(f'for {n=} and {k=} the number of possible combinations is:', sum(result), flush=True)

if __name__ == '__main__':
    combinations = generate_petersen_combinations()

    with ProcessPoolExecutor(max_workers=6) as e:
        futures = [e.submit(calculate_graph, *combination) for combination in combinations]
        result = [future.result() for future in futures]
```

# Petersen Graph
Petersenov graf alebo aj GP(5,2)/GP(5,3) by mal obsahovat 240 roznych hamiltonovskych ciest co obsahoval aj v nasom pripade
# Prism Graph
![](assets/Pasted%20image%2020230509092824.png)
pocet roznuch hamiltonovskych ciest pre Prism Grafy alebo aj GP(n, 1) sa da vypocitat podla vzorca uvedeneho nizsie tieto vysledky sedeli aj s nasim vypoctom
![](assets/Pasted%20image%2020230509092348.png)
| n   | k   | reference | ours    | coputation time (seconds) |
| --- | --- | --------- | ------- | ------------------------- |
| 3   | 1   | 60        | 60      | 0.241165                  |
| 4   | 1   | 144       | 144     | 0.408234                  |
| 5   | 1   | 260       | 260     | 0.430605                  |
| 6   | 1   | 456       | 456     | 0.449489                  |
| 7   | 1   | 700       | 700     | 0.450289                  |
| 8   | 1   | 1056      | 1056    | 0.523570                  |
| 9   | 1   | 1476      | 1476    | 0.637742                  |
| 10  | 1   | 2040      | 2040    | 0.851431                  |
| 11  | 1   | 2684      | 2684    | 1.376742                  |
| 12  | 1   | 3504      | 3504    | 2.436808                  |
| 13  | 1   | 4420      | 4420    | 4.570201                  |
| 14  | 1   | 5544      | 5544    | 9.193341                  |
| 15  | 1   | 6780      | 6780    | 18.876013                 |
| 16  | 1   | 8256      | 8256    | 38.582004                 |
| 17  | 1   | 9860      | 9860    | 80.748787                 |
| 18  | 1   | 11736     | 11736   | 167.125309                |
| 19  | 1   | 13756     | 13756   | 352.925756                |
| 20  | 1   | 16080     | 16080   | 720.918311                |
| 21  | 1   | 18564     | 18564   | 1525.202365               |
| 22  | 1   | 21384     | 21384   | 3117.319549               |
| 23  | 1   | 24380     | 24380   | 6504.590353               |
| 24  | 1   | 27744     | 27744   | 13323.631864              |
| 5   | 2   | 240       | 240     | 0.428004                  |
| 6   | 2   | ?         | 396     | 0.442183                  |
| 7   | 2   | ?         | 840     | 0.463994                  |
| 8   | 2   | ?         | 1280    | 0.527810                  |
| 9   | 2   | ?         | 1908    | 0.681121                  |
| 9   | 3   | ?         | 1440    | 0.628815                  |
| 10  | 2   | ?         | 3240    | 0.986918                  |
| 10  | 3   | ?         | 4560    | 1.021272                  |
| 10  | 4   | ?         | 3820    | 1.022082                  |
| 11  | 2   | ?         | 4444    | 1.641096                  |
| 11  | 3   | ?         | 5852    | 1.831548                  |
| 12  | 2   | ?         | 6864    | 3.036138                  |
| 12  | 4   | ?         | 4320    | 2.703661                  |
| 12  | 3   | ?         | 10800   | 3.344000                  |
| 13  | 2   | ?         | 9360    | 6.181629                  |
| 13  | 3   | ?         | 14352   | 7.163242                  |
| 13  | 4   | ?         | 14352   | 7.212957                  |
| 14  | 2   | ?         | 14476   | 12.568146                 |
| 14  | 3   | ?         | 23576   | 15.628240                 |
| 14  | 4   | ?         | 19964   | 16.065703                 |
| 14  | 6   | ?         | 21196   | 15.277588                 |
| 15  | 2   | ?         | 18180   | 26.378634                 |
| 15  | 5   | ?         | 11700   | 22.360309                 |
| 15  | 3   | ?         | 31200   | 31.441359                 |
| 16  | 2   | ?         | 28608   | 53.710715                 |
| 16  | 3   | ?         | 56704   | 71.173323                 |
| 16  | 4   | ?         | 41920   | 65.432103                 |
| 16  | 5   | ?         | 56704   | 70.629252                 |
| 16  | 6   | ?         | 45312   | 76.964597                 |
| 17  | 2   | ?         | 35156   | 113.397752                |
| 17  | 3   | ?         | 71876   | 154.238124                |
| 17  | 4   | ?         | 56576   | 161.658762                |
| 17  | 5   | ?         | 68816   | 165.071179                |
| 18  | 2   | ?         | 53748   | 231.499412                |
| 18  | 6   | ?         | 28908   | 198.059039                |
| 18  | 3   | ?         | 120024  | 316.207929                |
| 18  | 4   | ?         | 101124  | 355.914759                |
| 18  | 5   | ?         | 128376  | 363.362981                |
| 18  | 7   | ?         | 128376  | 364.007267                |
| 18  | 8   | ?         | 96588   | 325.722050                |
| 19  | 2   | ?         | 65588   | 484.809234                |
| 19  | 3   | ?         | 156788  | 705.110782                |
| 19  | 6   | ?         | 156788  | 694.230543                |
| 19  | 4   | ?         | 136572  | 761.324270                |
| 20  | 2   | ?         | 100160  | 965.642433                |
| 20  | 3   | ?         | 243360  | 1408.705578               |
| 20  | 5   | ?         | 244800  | 1222.730053               |
| 20  | 4   | ?         | 170960  | 1337.686183               |
| 20  | 8   | ?         | 207280  | 1338.678296               |
| 20  | 6   | ?         | 208880  | 1372.157722               |
| 21  | 2   | ?         | 119028  | 2022.837532               |
| 21  | 3   | ?         | 329448  | 3108.589124               |
| 21  | 4   | ?         | 289212  | 3494.053835               |
| 21  | 5   | ?         | 289212  | 3509.220519               |
| 21  | 6   | ?         | 313824  | 3680.935078               |
| 22  | 2   | ?         | 182072  | 3977.000451               |
| 22  | 3   | ?         | 511016  | 6548.145093               |
| 22  | 4   | ?         | 390852  | 7502.294494               |
| 22  | 7   | ?         | 511016  | 6529.962459               |
| 22  | 5   | ?         | 567776  | 7771.521561               |
| 22  | 6   | ?         | 500632  | 7830.907929               |
| 22  | 8   | ?         | 417076  | 7495.609020               |
| 22  | 10  | ?         | 388300  | 6332.507047               |
| 23  | 2   | ?         | 214728  | 8103.876592               |
| 23  | 3   | ?         | 671876  | 13651.828431              |
| 23  | 4   | ?         | 579140  | 15907.490406              |
| 23  | 5   | ?         | 676936  | 16677.499550              |
| 23  | 7   | ?         | 597448  | 15673.347977              |
| 24  | 2   | ?         | 324960  | 16144.131434              |
| 24  | 3   | ?         | 1033248 | 28175.226325              |
| 24  | 4   | ?         | 777312  | 32200.238381              |
| 24  | 6   | ?         | 724320  | 26888.100814              |
| 24  | 8   | ?         | 163200  | 13504.942768              |
| 24  | 9   | ?         | 1132608 | 35858.169003              |
| 24  | 10  | ?         | 1031328 | 35832.653079              |

# Hamiltonial Cycles
Pre vyhladanie cyklov oproti cestam jedina zmena bola ze koniec cesty musi byt susedny zo zaciatocnym bodom. Tento fakt nam vedel aj vyrazne urychlit vyhladavanie nakolko sme vedeli stopnut prehladavanie cesty hned ako sme navstivili vsetky 3 susedne body zaciatocnemu a dlzka aktualnej prehladanej cesty nebola `n*2`.

```python
def traverse(move_, target_len):
    paths = []
    
    if min([position in move_.path for position in move_.end_positions]):
        return paths
    
    for next_move in move_.next_moves:
        paths.extend(traverse(move_.move(next_move), target_len))
    
    if len(move_.path)==target_len and move_.path[-1] in move_.end_positions:
        return move_.end().path
    return paths
```

V porovnani z cestami kde kazdy vseobecny petersenov graf mal hamiltonovske cesty, cykly v urcitou periodicitou neexistovali. "The generalized Petersen graph GP(n,k) is nonhamiltonian iff k=2 and n=5 (mod 6)." 
Toto bola pravda aj v nasom pripade kde pre n=5,11,17 neexistovali hamiltonovske cykli.

## Vysledky poctov hamiltonovskych cyklov
| n   | k   | reference | ours  | coputation time (seconds) |
| --- | --- | --------- | ----- | ------------------------- |
| 4   | 1   |           | 96    | 0.455869                  |
| 3   | 1   |           | 36    | 0.460782                  |
| 5   | 1   |           | 100   | 0.468737                  |
| 5   | 2   |     0     | 0     | 0.466220                  |
| 6   | 1   |           | 192   | 0.485868                  |
| 6   | 2   |           | 144   | 0.481626                  |
| 7   | 1   |           | 196   | 0.476064                  |
| 7   | 2   |           | 196   | 0.487527                  |
| 8   | 1   |           | 320   | 0.517043                  |
| 8   | 2   |           | 384   | 0.550403                  |
| 9   | 1   |           | 324   | 0.624943                  |
| 9   | 2   |           | 108   | 0.720161                  |
| 9   | 3   |           | 324   | 0.661596                  |
| 10  | 1   |           | 480   | 0.823074                  |
| 10  | 2   |           | 1200  | 0.967824                  |
| 10  | 3   |           | 960   | 1.041399                  |
| 10  | 4   |           | 1200  | 1.004755                  |
| 11  | 1   |           | 484   | 1.255898                  |
| 11  | 2   |     0     | 0     | 1.578715                  |
| 11  | 3   |           | 484   | 1.715502                  |
| 12  | 1   |           | 672   | 2.123108                  |
| 12  | 2   |           | 1632  | 2.808668                  |
| 12  | 4   |           | 288   | 2.432993                  |
| 12  | 3   |           | 3264  | 2.996184                  |
| 13  | 1   |           | 676   | 3.936063                  |
| 13  | 2   |           | 676   | 5.588144                  |
| 13  | 3   |           | 1352  | 6.626280                  |
| 13  | 4   |           | 1352  | 6.613986                  |
| 14  | 1   |           | 896   | 8.013618                  |
| 14  | 2   |           | 3136  | 11.203421                 |
| 14  | 3   |           | 4928  | 14.143480                 |
| 14  | 4   |           | 3136  | 14.667567                 |
| 14  | 6   |           | 3920  | 13.995547                 |
| 15  | 1   |           | 900   | 16.237677                 |
| 15  | 2   |           | 180   | 23.321237                 |
| 15  | 5   |           | 1980  | 19.141817                 |
| 15  | 3   |           | 4500  | 28.333897                 |
| 16  | 1   |           | 1152  | 33.088867                 |
| 16  | 2   |           | 6912  | 46.946948                 |
| 16  | 3   |           | 9600  | 63.765646                 |
| 16  | 4   |           | 5120  | 57.005368                 |
| 16  | 5   |           | 9600  | 62.748709                 |
| 16  | 6   |           | 6912  | 67.935986                 |
| 17  | 1   |           | 1156  | 68.175547                 |
| 17  | 2   |     0     | 0     | 98.694220                 |
| 17  | 3   |           | 6936  | 135.432448                |
| 17  | 4   |           | 2312  | 141.746886                |
| 17  | 5   |           | 6936  | 145.729229                |
| 18  | 1   |           | 1440  | 141.137059                |
| 18  | 2   |           | 10800 | 198.127434                |
| 18  | 6   |           | 1296  | 165.453207                |
| 18  | 3   |           | 22752 | 278.029090                |
| 18  | 4   |           | 15552 | 310.948639                |
| 18  | 5   |           | 18720 | 320.145103                |
| 18  | 7   |           | 18720 | 317.919685                |
| 18  | 8   |           | 10800 | 281.852237                |
| 19  | 1   |           | 1444  | 294.020837                |
| 19  | 2   |           | 1444  | 407.400969                |
| 19  | 3   |           | 11552 | 600.777506                |
| 19  | 6   |           | 11552 | 602.978539                |
| 20  | 1   |           | 1760  | 605.183539                |
| 19  | 4   |           | 11552 | 667.242532                |
| 20  | 2   |           | 19520 | 816.096856                |
| 20  | 3   |           | 34880 | 1270.925939               |
| 20  | 5   |           | 42880 | 1171.717364               |
| 20  | 4   |           | 19200 | 1317.479569               |
| 20  | 8   |           | 24000 | 1380.640520               |
| 20  | 6   |           | 25920 | 1422.711107               |
| 21  | 1   |           | 1764  | 1244.895826               |
| 21  | 2   |           | 252   | 1674.534927               |
| 21  | 3   |           | 33516 | 2617.584773               |
| 22  | 1   |           | 2112  | 2577.949292               |
| 21  | 4   |           | 16128 | 2992.610506               |
| 21  | 5   |           | 16128 | 3001.815784               |
| 21  | 6   |           | 17640 | 3139.931567               |
| 22  | 2   |           | 36784 | 3334.439787               |
| 22  | 3   |           | 58432 | 5523.159431               |

### Ukazkova cesta pre GP(22, 3)
0,22,41,38,35,13,12,11,33,36,14,15,16,17,39,42,20,19,18,40,37,34,31,9,10,32,29,7,8,30,27,5,6,28,25,3,4,26,23,1,2,24,43,21,0
![](assets/Pasted%20image%2020230510214622.png)
