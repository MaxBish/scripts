import ldap3
import argparse
import sys

server = ldap3.Server('ldaps://specific LDAP server')
conn = ldap3.Connection(server)
conn.bind()
basedn = 'dc=foobar,dc=dorq,dc=baz'
attribs = ['department']

parser=argparse.ArgumentParser(
    description ='searches the LDAP server and returns department. Accepts any partial entry', 
    usage='usearch3 PARTIAL_MATCH (name, username)',
    formatter_class = argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('istr', help='searches stuff')
parser.print_help
args = parser.parse_args(None if sys.argv[1:] else ['-h'])

str1 = args.istr

sfilter = "(|(department=*{}*))".format(str1)

conn.search(basedn,sfilter)
conn.search(basedn,sfilter,attributes = attribs)

leng = len(conn.entries)
for i in range(leng):
   
    user = conn.entries[i].uid
    fullname = conn.entries[i].cn
    department = conn.entries[i].department
    
    print("user:\t{}\nname:\t{}\nemail:\t{}\n\n".format(user,fullname,email)) 
