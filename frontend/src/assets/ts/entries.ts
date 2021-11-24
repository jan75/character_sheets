import { getRequest, postRequest, MultiDataResponse } from './network'
import { Series } from './series'
import { EntryType } from './entrytypes'

interface Entry {
    id: number,
    name: string,
    date: string,
    order_in_series: number,
    series: Series,
    entrytype: EntryType
}

interface EntryInputData {
    name: string,
    date: string,
    order_in_series: number,
    seriesId: number,
    entrytypeId: number
}

const createEntry = async (data: EntryInputData): Promise<void> => {
    return postRequest<EntryInputData>('http://localhost:5000/rest/entries', data);
}

const getEntriesList = async (offset: number): Promise<MultiDataResponse<Entry>>  => {
    const url = `http://localhost:5000/rest/entries?offset=${offset}`;
    return getRequest<MultiDataResponse<Entry>>(url);
}

const getEntry = async (id: number): Promise<Entry> => {
    const url = `http://localhost:5000/rest/entries/${id}`
    return getRequest<Entry>(url);
}

export { Entry, EntryInputData, createEntry, getEntriesList, getEntry }