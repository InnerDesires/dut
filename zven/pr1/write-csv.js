const fs = require('fs'); // Вбудований модуль для роботи з файлами

// Функція для обчислення y = sin(x) / x
const calculateFunction = (x) => (x === 0 ? 1 : Math.sin(x) / x);

// Генеруємо дані
const generateData = () => {
    const data = [];
    for (let x = -10; x <= 10; x += 0.1) { // Крок 0.1 для більшої точності
        const y = calculateFunction(x);
        data.push({ x: x.toFixed(2), y: y.toFixed(4) });
    }
    return data;
};

// Створюємо CSV контент
const createCsvContent = (data) => {
    let csv = 'x,y\n'; // Заголовки стовпців
    data.forEach(row => {
        csv += `${row.x},${row.y}\n`;
    });
    return csv;
};

// Записуємо у файл
const saveCsvFile = (filename, content) => {
    fs.writeFileSync(filename, content, 'utf8');
    console.log(`Файл ${filename} успішно створено!`);
};

// Основний процес
const main = () => {
    const data = generateData();
    const csvContent = createCsvContent(data);
    saveCsvFile('function_data.csv', csvContent);
};

main();
