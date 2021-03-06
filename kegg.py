#Makes list of all EC present in swissprot register
def make_ec_list():
    ec_list = []
    for ss in sse:
        found = re.search('EC=(.+?) {', ss.description)
        if found != None:
            ec_list.append(found.group(1))
    return ec_list
    
#Requests enzyme register from KEGG
def make_kegg():
    present = 0
    ec_list = make_ec_list()
    for ec in ec_list:
        try:
            request = REST.kegg_get(ec)
            open("ec_"+ec+".txt", 'wb').write(request.read())
            present += 1
        except:
            print('kegg request failed')
    return present
 
#Reads a file and returns list of lines
def read_kegg(ec):
    linhas = list()
    file = open("ec_"+ec+".txt")
    temp = file.readlines()
    for linha in temp:
        linhas.append(linha.rstrip('\n'))
    return linhas

#Creates table with information from KEGG    
def read_all_kegg():
    ec_list = make_ec_list()
    with open('kegg_table.txt','w') as kt:
        kt.write('<table style="width:100%"><tr>')
        heads = ['NCBI id','KEGG id', 'EC number','KEGG Orthology', 'KEGG reaction ID','KEGG pathway']
        linha = str()    
        for head in heads:
            linha += '<th>'+head+'</th>'
        kt.write(linha)
        for ec in make_ec_list(sse):
            linha = '<tr>'
            for entry in sse:
                if ec in entry.description:
                    for ref in entry.cross_references:
                        if ref[0] == 'RefSeq':
                            first = ref[2]
                        if ref[0] == 'KEGG':
                            found = re.search(':(TP_[0-9]{4})', ref[1])
                            if found != None:
                                second = found.group(1)
                            else:
                                found = re.search(':(TPANIC_[0-9]{4})', ref[1])
                                if found != None:
                                    second = found.group(1)
                                else:
                                    second = '-'
                    try:
                        record = read_kegg(ec)
                        found = re.search('EC (.+?)\s', record[0])            
                        if found != None:
                            third = found.group(1)
                        else:
                            third = '-'
                        pathways = []                            
                        for line in record:
                            pathway = False
                            if line.startswith('PATHWAY'):
                                pathway = True
                                found = re.search('\sec[0-9]+\s+(.+)', line)
                                if found != None:
                                    pathways.append(found.group(1))
                            else:
                                if pathway == True:
                                    found = re.search('\sec[0-9]+\s(.+)', line)
                                    if found == None:
                                        pathway = False
                                    else:
                                        pathways.append(found.group(1))
                            if line.startswith('REACTION'):
                                found = re.search('RN:(R[0-9]+)', line)
                                if found != None:
                                    fifth = found.group(1)
                                else:
                                    fifth = '-'
                            if line.startswith('ORTHOLOGY'):
                                found = re.search('ORTHOLOGY\s+(.+)', line) 
                                if found != None:
                                    fourth = found.group(1)
                                else:
                                    fourth = '-'
                        sixth = ''
                        for i in pathways:
                            sixth += i + '; '
                            sixth = sixth.rstrip('; ')
                    except:
                        third = ec
                        fourth = '-'
                        fifth = '-'
                        sixth = '-'
                    print(first,second,third,fourth,fifth,sixth)
                    linha += '<td>'+str(first)+'</td>'          #NCBI ID
                    linha += '<td>'+str(second)+'</td>'         #KEGG ID
                    linha += '<td>'+third+'</td>'               #EC numbers list
                    linha += '<td>'+fourth+'</td>'              #KEGG ortholog
                    linha += '<td>'+fifth+'</td>'               #Reaction ID
                    linha += '<td>'+sixth+'</td>'               #KEGG pathways
                    linha += '</tr>'
                    kt.write(linha)
        kt.write('</tr></table>')
        kt.close()
