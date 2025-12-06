# React + Vite

Ce modèle fournit une configuration minimale pour faire fonctionner React avec Vite avec HMR et quelques règles ESLint.

Actuellement, deux plugins officiels sont disponibles :

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) utilise [Babel](https://babeljs.io/) (ou [oxc](https://oxc.rs) lorsqu'il est utilisé dans [rolldown-vite](https://vite.dev/guide/rolldown)) pour Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) utilise [SWC](https://swc.rs/) pour Fast Refresh

## Compilateur React

Le compilateur React n'est pas activé sur ce modèle en raison de son impact sur les performances de développement et de build. Pour l'ajouter, consultez [cette documentation](https://react.dev/learn/react-compiler/installation).

## Étendre la configuration ESLint

Si vous développez une application de production, nous recommandons d'utiliser TypeScript avec des règles de lint conscientes des types activées. Consultez le [modèle TS](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) pour des informations sur la façon d'intégrer TypeScript et [`typescript-eslint`](https://typescript-eslint.io) dans votre projet.
