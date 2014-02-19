__date__ = "July 27, 2013"
__author__ = "AlienOne"
__copyright__ = "GPL"
__credits__ = ["AlienOne", "zer0h0ur"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "AlienOne"
__email__ = "ali3n0ne@alienone.org"
__status__ = "Prototype"


import requests
from py2neo import neo4j
from pandas import DataFrame
from itertools import groupby


def getData():
    """Get CSV Mandiant Data Set - output list data structure"""
    response = requests.get("https://raw.github.com/alienone/OSINT/master/MANDIANTAPT/APT-Maxmind-Enrichment-Product-2013-07-14-09-25-42.csv")
    iterResponse = response.iter_lines()
    next(iterResponse)
    for line in iterResponse:
        yield line.split(',')


def create_nodes(args=list):
    """Create list of dicts - each dict will represent a node"""
    list_dicts = []
    for prodList in getData():
        if len(prodList[0]) != 0:
            dict_object = dict(zip(args, prodList))
            list_dicts.append(dict_object)
    return list_dicts


def clusterData(args, column_name):
    """Leverage Panadas Groupby to cluster nodes by ASN - Then convert resulting DataFrames into list dicts by cluster"""
    gd = DataFrame(create_nodes(args)).groupby(column_name)
    asn_groups = [x[0] for x in gd]
    for asn in asn_groups:
        df = gd.get_group(asn)
        create_dict = [{k: df.values[i][v] for v, k in enumerate(df.columns)} for i in range(len(df))]
        yield create_dict


def normalize_cluster(cluster):
    normalized_cluster = {'ASN': [], 'FQDN': []}
    del normalized_cluster['ASN'][:]
    del normalized_cluster['FQDN'][:]
    for node in cluster:
        for k, v in node.items():
            normalized_cluster[k].append(v)
    return normalized_cluster


def main():
    """Batch create nodes and node relationships in Neo4j"""
    # graph_db = neo4j.GraphDatabaseService("http://192.168.2.2:7474/db/data/")
    results_list = []
    args = ["FQDN", "ASN"]
    column_name = 'ASN'
    for cluster in clusterData(args, column_name):
        results_list.append(normalize_cluster(cluster))
    for item in results_list:
        print(list(set(item['ASN'])), list(set(item['FQDN'])))


if __name__ == '__main__':
    main()
