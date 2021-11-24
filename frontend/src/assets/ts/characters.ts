import { getRequest, postRequest, MultiDataResponse } from './network'
import { Series } from './series';

interface Character {
    name: string,
    occursFirstInEntryId: number,
    series: Series
}

interface CharacterInputData {
    name: string,
    occursFirstInEntryId: number,
    seriesId: number
}

const createCharacter = async (data: CharacterInputData): Promise<void> => {
    return postRequest<CharacterInputData>('http://localhost:5000/rest/characters', data);
}

const getCharacterList = async (offset: number): Promise<MultiDataResponse<Character>>  => {
    const url = `http://localhost:5000/rest/characters?offset=${offset}&limit=100`;
    return getRequest<MultiDataResponse<Character>>(url);
}

const searchCharacterList = async (name: string, offset: number): Promise<MultiDataResponse<Character>> => {
    const url = `http://localhost:5000/rest/characters/search?q=${name}&offset=${offset}`
    return getRequest<MultiDataResponse<Character>>(url);
}

const getCharacter = async (id: number): Promise<Character> => {
    const url = `http://localhost:5000/rest/characters/${id}`;
    return getRequest<Character>(url);
}

export { Character, CharacterInputData, createCharacter, getCharacterList, getCharacter }