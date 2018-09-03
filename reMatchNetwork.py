from __future__ import print_function
from ortools.graph import pywrapgraph
from enum import Enum, unique


@unique
class NodeType(Enum):
    # TODO: support for more type of supplys
    Battery = 0
    Solar = 2
    BioMass = 3
    Demand = 1


class reMatchNetwork:
    operationTime = 24
    networkCostFlowSolver = pywrapgraph.SimpleMinCostFlow()
    numberOfSupply = {_supply_type: 0 for _name, _supply_type in NodeType.__members__.items()}

    def __init__(self, supplyProfiles, supplyCosts, demandProfiles):
        """build network for ReMatch flow model:

        Input: List of Dictionary contains {supply type: [supply capaliticy]}
        List contains {demand sr.no :[demand profile]}

        use other method to manipulate building decisions
        """
        self.supplyTypes = 0
        self.demandTypes = 0
        self.DemandNodes = list()
        self.SupplyNodes = list()

        self.demandProfiles = demandProfiles
        self.numberOfDemands = len(demandProfiles)

        self.supplyProfiles = supplyProfiles
        self.supplyCosts = supplyCosts

    def addSupply(self, typeOfSupply):
        supplySerial = self.numberOfSupply[typeOfSupply]
        self.numberOfSupply[typeOfSupply] += 1
        supplyUID = self.nodeUID(typeOfSupply, supplySerial)

        if typeOfSupply == NodeType.Battery:
            for time in range(self.operationTime - 1):
                for sup in self.SupplyNodes:
                    self.networkCostFlowSolver.AddArcWithCapacityAndUnitCost(sup | time, supplyUID | time,
                                                                             self.supplyProfiles[NodeType.Battery][
                                                                                 time],
                                                                             self.supplyCosts[NodeType.Battery][time])
                self.networkCostFlowSolver.AddArcWithCapacityAndUnitCost(supplyUID | time, supplyUID | (time + 1),
                                                                         999999, 0)
                for i in range(self.numberOfDemands):
                    self.networkCostFlowSolver.AddArcWithCapacityAndUnitCost(supplyUID | time,
                                                                             self.nodeUID(NodeType.Demand, i) | time,
                                                                             999999, 0)
            return

        for time in range(self.operationTime):
            for i in range(self.numberOfDemands):
                self.networkCostFlowSolver.AddArcWithCapacityAndUnitCost(supplyUID | time,
                                                                         self.nodeUID(NodeType.Demand, i) | time,
                                                                         999999, 0)
            self.networkCostFlowSolver.AddArcWithCapacityAndUnitCost(0, supplyUID | time,
                                                                     self.supplyProfiles[typeOfSupply][time],
                                                                     self.supplyCosts[typeOfSupply][time])
            for i in range(self.numberOfSupply[NodeType.Battery]):
                self.networkCostFlowSolver.AddArcWithCapacityAndUnitCost(supplyUID | time,
                                                                         self.nodeUID(NodeType.Battery, i) | time,
                                                                         self.supplyProfiles[NodeType.Battery][time],
                                                                         self.supplyCosts[NodeType.Battery][time])
        self.SupplyNodes.append(supplyUID)

    def solve(self):
        totalDemand = 0
        for i in range(self.numberOfDemands):
            for time in range(self.operationTime):
                self.networkCostFlowSolver.SetNodeSupply(self.nodeUID(NodeType.Demand, i) | time,
                                                         0 - self.demandProfiles[i][time])
                totalDemand += self.demandProfiles[i][time]
        self.networkCostFlowSolver.SetNodeSupply(0, totalDemand)
        if self.networkCostFlowSolver.Solve() == self.networkCostFlowSolver.OPTIMAL:
            # self._debug_print()
            return self.networkCostFlowSolver.OptimalCost()
        else:
            return float('Inf')

    def _debug_print(self):
        min_cost_flow = self.networkCostFlowSolver
        print('Minimum cost:', min_cost_flow.OptimalCost())
        print('')
        print('  Arc          Flow / Capacity  Cost')
        for i in range(min_cost_flow.NumArcs()):
            cost = min_cost_flow.Flow(i) * min_cost_flow.UnitCost(i)
            print('%3s -> %3s   %3s  / %10s       %3s' % (
                min_cost_flow.Tail(i),
                min_cost_flow.Head(i),
                min_cost_flow.Flow(i),
                min_cost_flow.Capacity(i),
                cost))

    @staticmethod
    def nodeUID(typeOfNode, nodeSerial):
        """set a UID for a node v_{t,r} as Solver require node have an integer ID"""
        return (nodeSerial << 8) | (typeOfNode.value << 6) | (1 << 5)


if __name__ == "__main__":
    testinput1 = {NodeType.Solar: [0, 0, 0, 0, 0, 1, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 1, 0, 0, 0, 0, 0, 0],
                  NodeType.BioMass: [3 for i in range(24)], NodeType.Battery: [100 for i in range(24)]}
    testinput2 = {NodeType.Solar: [0 for i in range(24)], NodeType.BioMass: [2 for i in range(24)],
                  NodeType.Battery: [0 for i in range(24)]}
    testnetwork = reMatchNetwork(testinput1, testinput2, [[1 for i in range(24)]])
    testnetwork.addSupply(NodeType.Solar)
    testnetwork.addSupply(NodeType.Battery)
    testnetwork.addSupply(NodeType.BioMass)
    print(testnetwork.solve())
