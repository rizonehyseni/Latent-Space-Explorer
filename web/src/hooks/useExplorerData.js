import { useCallback, useEffect, useState } from 'react'

import { loadExplorerData } from '../data/loadExplorerData.js'

const initialState = {
  status: 'loading',
  data: null,
  error: null,
}

export function useExplorerData() {
  const [reloadKey, setReloadKey] = useState(0)
  const [state, setState] = useState(initialState)

  useEffect(() => {
    const controller = new AbortController()


    loadExplorerData({
      signal: controller.signal,
    })
      .then((data) => {
        if (!controller.signal.aborted) {
          setState({
            status: 'success',
            data,
            error: null,
          })
        }
      })
      .catch((error) => {
        if (
          !controller.signal.aborted &&
          error.name !== 'AbortError'
        ) {
          setState({
            status: 'error',
            data: null,
            error,
          })
        }
      })

    return () => {
      controller.abort()
    }
  }, [reloadKey])

    const retry = useCallback(() => {
    setState(initialState)
    setReloadKey((currentKey) => currentKey + 1)
  }, [])

  return {
    ...state,
    retry,
  }
}