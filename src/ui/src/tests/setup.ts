import '@testing-library/jest-dom'
import { server } from './mocks/server'

// jsdom does not implement HTMLDialogElement.showModal / close.
// Polyfill so Modal tests work without a real browser.
HTMLDialogElement.prototype.showModal = function () {
  this.setAttribute('open', '')
}
HTMLDialogElement.prototype.close = function () {
  this.removeAttribute('open')
}

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())
