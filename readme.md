![](assets/Pasted%20image%2020230509092647.png)

# Process

## logical deconstruction
![](assets/Pasted%20image%2020230509093312.png)

### starting positions

```python
in_in = (n, n+k)
in_out = (n, 0)
out_in = (0, n)
out_out = (0, 1)
```

## possible combinations for each starting position
```
out_out
0,1 | 1,0 | 2,1
0,2 | 1,2 | 2,0

out_in
0,3 | 1,4 | 2,5

in_out
3,0 | 4,1 | 5,2

in_in
3,4 | 4,3 | 5,3
3,5 | 4,5 | 5,4
```

generalized:
```
in_in -> 2*n 
in_out -> n 
out_in -> n 
out_out -> 2*n
```

## Base
```python
@dataclass
class Move():
    path: list[int] = field(default_factory=list, init=False)
    position: tuple = field(default_factory=tuple, init=False)
    next_moves: list[tuple()] = field(default_factory=list[tuple()], init=False)
    possible_moves: list[tuple()] = field(default_factory=list[tuple()])

    def __post_init__(self):
        self.next_moves = [item for move in self.possible_moves for item in move]

    def overwrite_next_moves(self, next_moves):
        self.next_moves = next_moves
        return self

    def move(self, position: tuple):
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

### generate adjacency matrix

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
        # adj_matrix[x_out, y_in] = 1
        # adj_matrix[y_in, x_out] = 1

        adj_matrix[x_out, x_in] = 1
        adj_matrix[x_in, x_out] = 1

    return adj_matrix
```

### computation
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
petersen graph or GP(5,2)/GP(5,3) based on textbooks should have 120 distinct paths our results

for n=5 and k=2:
* is: 240
* time to compute: 0.428004 seconds

# Prism graphs
![](assets/Pasted%20image%2020230509092824.png)
The numbers of directed Hamiltonian paths for prism graphs in generalized petersen graph notation graphs GP(n, 1) ca be calculated by:
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
