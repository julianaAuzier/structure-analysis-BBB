import os
import pandas as pd
from Bio import SeqIO
from rdkit import Chem
import filter
from calcRdkit import calc
from calcMordred import calcSpecific

# data for test
basePDB = os.getcwd() + '/data/1pef.pdb'
baseMol = os.getcwd() + '/data/mol_files/BBB+/mol_18.mol'
baseCSV = os.getcwd() + '/data/brainPeps.csv'

# descriptors calculated in dichiara dataset
descriptors = ['weight','logP', 'TPSA(Tot)', 'HBA', 'HBD', 'nN', 'nO', 'n(N+O)']

# folder to save Rdkit Results
if not os.path.exists("RdkitResults"):
    os.makedirs("RdkitResults")

# folder to save Mordred Results
if not os.path.exists("MordredResults"):
    os.makedirs("MordredResults")

def descriptorsRdkit(data, colPeptides ='peptides', colKeep = None):
    ext = (os.path.basename(data)).split('.')[-1]

    # for pdb files
    if ext == 'pdb':
        chain = {record.id: record.seq for record in SeqIO.parse(data, 'pdb-seqres')}
        for k, v in chain.items():
            seqPDB = v
            naturalPep = filter.naturalPep(seqPDB)

        if naturalPep is not False:
            molPDB = Chem.MolFromPDBFile(data)
            PDBresult = pd.DataFrame(calc(molPDB)).T
            PDBresult.columns = descriptors
            return PDBresult.to_csv('RdkitResults/PDBresult.csv', index=False)
        else:
            print("Error: Not natural peptide!")

    # for mol files (cannot extract sequence for filter)
    elif ext == 'mol':
        molMol = Chem.MolFromMolFile(data)
        MOLresult = pd.DataFrame(calc(molMol)).T
        MOLresult.columns = descriptors
        return MOLresult.to_csv('RdkitResults/MOLresult.csv',index=False)

    # for csv files
    elif ext == 'csv':
        molCSV = pd.read_csv(data)
        results = []

        for i in range(len(molCSV)):
            # removing break lines (don't always need)
            molCSV.iloc[i][colPeptides] = str(molCSV.iloc[i][colPeptides]).strip()

        # only natural peptide
        naturalmolCSV = []
        for x,y in zip(molCSV[colPeptides],molCSV[colKeep]):
            if filter.naturalPep(x) is not None:
                naturalmolCSV.append([x,y])
        naturalmolCSV = pd.DataFrame(naturalmolCSV)

        for i in range(len(naturalmolCSV)):
            results.append(calc(Chem.MolFromSequence(naturalmolCSV[0][i])))

        CSVresult = pd.concat([naturalmolCSV, pd.DataFrame(results)], axis=1)
        CSVresult.columns = [colPeptides] + [colKeep] + descriptors
        print("The Rdkit Results refer only to natural peptides.")
        return CSVresult.to_csv('RdkitResults/CSVresult.csv', index=False)
    else:
        return 'Unsupported file type.'

def descriptorsMordred(data, colPeptides ='peptides', colKeep = None):
    ext = (os.path.basename(data)).split('.')[-1]

    # for pdb files
    if ext == 'pdb':
        chain = {record.id: record.seq for record in SeqIO.parse(data, 'pdb-seqres')}
        for k, v in chain.items():
            seqPDB = v
            naturalPep = filter.naturalPep(seqPDB)

        if naturalPep is not False:
            molPDB = Chem.MolFromPDBFile(data)
            PDBresult = pd.DataFrame(calcSpecific(molPDB)).T
            PDBresult.columns = descriptors
            return PDBresult.to_csv('MordredResults/PDBresult.csv', index=False)
        else:
            print("Error: Not natural peptide!")

    # for mol files (cannot extract sequence for filter)
    elif ext == 'mol':
        molMol = Chem.MolFromMolFile(data)
        MOLresult = pd.DataFrame(calcSpecific(molMol)).T
        MOLresult.columns = descriptors
        return MOLresult.to_csv('MordredResults/MOLresult.csv',index=False)

    # for csv files
    elif ext == 'csv':
        molCSV = pd.read_csv(data)
        results = []

        for i in range(len(molCSV)):
            # removing break lines (don't always need)
            molCSV.iloc[i][colPeptides] = str(molCSV.iloc[i][colPeptides]).strip()

        # only natural peptide
        naturalmolCSV = []
        for x,y in zip(molCSV[colPeptides],molCSV[colKeep]):
            if filter.naturalPep(x) is not None:
                naturalmolCSV.append([x,y])
        naturalmolCSV = pd.DataFrame(naturalmolCSV)

        for i in range(len(naturalmolCSV)):
            results.append(calcSpecific(Chem.MolFromSequence(naturalmolCSV[0][i])))

        CSVresult = pd.concat([naturalmolCSV, pd.DataFrame(results)], axis=1)
        CSVresult.columns = [colPeptides] + [colKeep] + descriptors
        print("The Mordred Results refer only to natural peptides.")
        return CSVresult.to_csv('MordredResults/CSVresult.csv', index=False)
    else:
        return 'Unsupported file type.'


if __name__ == '__main__':
    descriptorsRdkit(baseMol)
    descriptorsRdkit(basePDB)
    descriptorsRdkit(baseCSV, 'onelettersequence', 'label')

    descriptorsMordred(baseMol)
    descriptorsMordred(basePDB)
    descriptorsMordred(baseCSV, 'onelettersequence', 'label')
