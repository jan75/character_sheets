import { getRequest, postRequest, MultiDataResponse } from './network'
import { Entry } from './entries'
import { Character } from './characters';

interface Series {
    id: number,
    name: string
}

interface SeriesInputData {
    name: string
}

const createSeries = async (data: SeriesInputData): Promise<void> => {
    return postRequest<SeriesInputData>('http://localhost:5000/rest/series', data);
}

const getSeriesList = async (offset: number): Promise<MultiDataResponse<Series>>  => {
    const url = 'http://localhost:5000/rest/series?offset=' + offset;
    return getRequest<MultiDataResponse<Series>>(url);
}

const searchSeriesList = async (name: string, offset: number): Promise<MultiDataResponse<Series>> => {    
    const url = `http://localhost:5000/rest/series/search?name=${name}&offset=${offset}`
    return getRequest<MultiDataResponse<Series>>(url);
}

const getSeriesEntries = async (seriesId: number, offset: number): Promise<MultiDataResponse<Entry>> => {
    const url = `http://localhost:5000/rest/series/${seriesId}/entries?offset=${offset}`;
    return getRequest<MultiDataResponse<Entry>>(url);
}

const searchSeriesEntries = async (seriesId: number, searchTerm: string, offset: number): Promise<MultiDataResponse<Entry>> => {
    const url = `http://localhost:5000/rest/series/${seriesId}/entries?q=${searchTerm}&offset=${offset}`
    return getRequest<MultiDataResponse<Entry>>(url);
}

const getSeriesCharacters = async (seriesId: number, offset: number): Promise<MultiDataResponse<Character>> => {
    const url = `http://localhost:5000/rest/series/${seriesId}/characters?offset=${offset}&limit=100`
    return getRequest<MultiDataResponse<Character>>(url);
}

const getSeries = async (id: number): Promise<Series> => {
    const url = 'http://localhost:5000/rest/series/' + id;
    return getRequest<Series>(url);
}

export { Series, SeriesInputData, createSeries, getSeries, getSeriesList, searchSeriesList, getSeriesEntries, getSeriesCharacters }