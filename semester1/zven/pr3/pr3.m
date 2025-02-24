% Навчальна вибірка A
x_train = 0:0.3:2*pi;
y_train = cos(x_train);
A = [x_train; y_train]';

% Тестова вибірка B
x_test = 0.1:0.6:(2*pi - 0.3);
y_test = cos(x_test);
B = [x_test; y_test]';

% Перевірочне значення
C = [0.8; cos(0.8)]';

disp(['Перевірочне значення: ', num2str(cos(0.8))]);

anfisedit;