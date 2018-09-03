from __future__ import print_function

from copy import deepcopy as copy

from reMatchNetwork import reMatchNetwork, NodeType


class reMatchPlan:
    """The Planer of ReMatch DER models with out scenario tree feature"""
    MaximumIteration = 100
    SupplyNumber = {_supply_type: 0 for _name, _supply_type in NodeType.__members__.items()}

    def __init__(self, supplyProfiles, supplyCosts, demandProfiles, supplyMaximum, supplyCapital):
        """

        :type supplyProfiles: dict
        :type supplyCosts: dict
        :type supplyCapital: dict
        :type supplyMaximum: dict
        :type demandProfiles: list(list)
        :rtype: reMatchPlan
        """
        # self.supplyProfiles = supplyProfiles
        # self.supplyCosts = supplyCosts
        # self.demandProfiles = demandProfiles
        self.supplyMaximum = supplyMaximum
        self.supplyCapital = supplyCapital
        self.supplyCapital[NodeType.Demand] = 0  # For possible inconvenience
        self.network = reMatchNetwork(supplyProfiles, supplyCosts, demandProfiles)

    def capital_cost(self, supply_number):
        """calculate capital cost given supply number dict"""
        cost = 0
        for _name, supply_type in NodeType.__members__.items():
            cost += supply_number[supply_type] * self.supplyCapital[supply_type]
        return cost

    def plan(self):
        """The Planner callable function"""
        cost_r = {supply_type: 0 for _name, supply_type in NodeType.__members__.items()}
        supply_types = [supply_type for _name, supply_type in NodeType.__members__.items()]
        supply_types.remove(NodeType.Demand)
        total_cost = float('Inf')

        for _n in range(self.MaximumIteration):
            network_back = self.network
            for supply_type in supply_types:
                before_cost_m = self.network.solve() + self.capital_cost(self.network.numberOfSupply)
                network_new = copy(self.network)
                for m in range(self.supplyMaximum[supply_type]):
                    network_back = copy(network_new)
                    network_back.addSupply(supply_type)
                    now_cost_m = network_back.solve() + self.capital_cost(network_back.numberOfSupply)
                    if now_cost_m > before_cost_m:
                        network_back = network_new
                        break
                    before_cost_m = now_cost_m
                cost_r[supply_type] = before_cost_m
            best_type = NodeType.Demand
            best_cost = float('Inf')
            for supply_type in supply_types:
                cost = cost_r[supply_type]
                (best_type, best_cost) = (supply_type, cost) if cost < best_cost else (best_type, best_cost)
            if total_cost > best_cost:
                self.network = network_back
                total_cost = best_cost
                supply_types.remove(best_type)
            else:
                break
        self.print_result(self.network)

    def print_result(self, network):
        for name, supply_type in NodeType.__members__.items():
            print("{} /  {}".format(name, network.numberOfSupply[supply_type]))
        print("================")
        self.network._debug_print()


# too tired, write tomorrow

def read_int_list(raw_list: str) -> list:
    return list(map(int, raw_list.split(",")))


if __name__ == '__main__':
    print('===Input profile===        ', end='')
    profile_demand = list()
    profile_cost   = dict()
    profile_supply = dict()
    profile_max = dict()
    capital = dict()
    for i in range(24):
        print('{0:>3s},'.format(str(i)), end='')
    print('')

    for name, supply_type in NodeType.__members__.items():
        if supply_type != NodeType.Demand:
            profile_raw: str = input('Input profile for  {0:>7s}:'.format(name))
            profile_supply[supply_type] = read_int_list(profile_raw)

            profile_raw: str = input('Input cost for  {0:>10s}:'.format(name))
            profile_cost[supply_type] = read_int_list(profile_raw)

            profile_max[supply_type] = int(input('Input maximum for {0}:'.format(name)))
            capital[supply_type]     = int(input('Input capital for {0}:'.format(name)))

        else:
            for i in range(int(input('Number of demands        :'))):
                profile_raw = input('Input Demand profiles     :')
                profile_demand.append(read_int_list(profile_raw))

    planner = reMatchPlan(profile_supply, profile_cost, profile_demand, profile_max, capital)
    planner.plan()
