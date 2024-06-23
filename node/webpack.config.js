const path = require('path');
const CopyPlugin = require("copy-webpack-plugin");

module.exports = {
    entry: {
        main: './src/index.js',
        lobby: './src/lobby.js',
    },
    output: {
        filename: '[name].js',
        path: path.resolve(__dirname, '../static/scripts'),
    },
    plugins: [
      new CopyPlugin({
          patterns: [
              { from: '../project/assets.png', to: '../images/assets.png' },
              { from: '../project/assets.json', to: '../images/assets.json' },
              { from: 'node_modules/bootstrap/dist/css/bootstrap.min.css', to: '../css/bootstrap.min.css' }
          ],
      }),
    ],
};
