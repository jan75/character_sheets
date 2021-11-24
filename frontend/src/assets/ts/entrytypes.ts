import { getRequest, postRequest, MultiDataResponse } from './network'
import { Entry } from './entries'

interface EntryType {
    id: number,
    name: string
}

interface EntryTypeInputData {
    name: string
}

const createEntryType = async (data: EntryTypeInputData): Promise<void> => {
    return postRequest<EntryTypeInputData>('http://localhost:5000/rest/entrytypes', data);
}

const getEntryTypeList = async (offset: number): Promise<MultiDataResponse<EntryType>>  => {
    const url = `http://localhost:5000/rest/entrytypes?offset=${offset}`;
    return getRequest<MultiDataResponse<EntryType>>(url);
}

const getEntryTypeEntries = async (entryTypeId: number, offset: number): Promise<MultiDataResponse<Entry>> => {
    const url = `http://localhost:5000/rest/entrytypes/${entryTypeId}/entries?offset=${offset}`;
    return getRequest<MultiDataResponse<Entry>>(url);
}

const getEntryType = async (id: number): Promise<EntryType> => {
    const url = `http://localhost:5000/rest/entrytypes/${id}`
    return getRequest<EntryType>(url);
}

export { EntryType, EntryTypeInputData, createEntryType, getEntryTypeList, getEntryTypeEntries, getEntryType }