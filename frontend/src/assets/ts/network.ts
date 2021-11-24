interface MultiDataResponse<T> {
  limit: number,
  offset: number,
  size: number,
  data: [T]
}

const getRequest = async <T>(url: string): Promise<T> => {
  console.log('getRequest:', url);

  const response = await fetch(url);
  if (response.ok) {
    const jsonValue = await response.json();
    return Promise.resolve(jsonValue);
  } else {
    return Promise.reject('Unexpected error');
  }
}

const postRequest = async <T>(url: string, data: T): Promise<void> => {
  console.log('postRequest:', url, data);
  const requestOptions = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  };

  const response = await fetch(url, requestOptions);
  if (response.ok) {
    return Promise.resolve();
  } else {
    if (response.status >= 400 && response.status < 500) {
      const jsonValue = await response.json();
      return Promise.reject(jsonValue['message']);
    } else {
      return Promise.reject('Unexpected error');
    }
  }
}


export { getRequest, postRequest, MultiDataResponse }

